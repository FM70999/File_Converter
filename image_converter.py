import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import img2pdf
import os
from pathlib import Path
import threading
import tkinter.font as tkfont

class DraggableListbox(tk.Listbox):
    def __init__(self, master, app, **kw):
        # Create a larger font
        default_font = tkfont.nametofont("TkTextFont")
        custom_font = tkfont.Font(
            family=default_font.cget("family"),
            size=int(default_font.cget("size") * 2)  # Double the default size, convert to integer
        )
        
        # Add the font to the keyword arguments
        kw['font'] = custom_font
        # Add some padding for better visibility
        kw['selectmode'] = tk.SINGLE
        kw['activestyle'] = 'none'  # Remove underline from active item
        
        super().__init__(master, **kw)
        self.app = app
        self.drag_data = {'item': None, 'index': None, 'y': 0}
        
        # Configure colors and appearance
        self.configure(
            selectbackground='#0078D7',  # Windows-style selection color
            selectforeground='white',
            background='white',
            foreground='black'
        )
        
        # Bind mouse events
        self.bind('<Button-1>', self.on_click)
        self.bind('<B1-Motion>', self.on_drag)
        self.bind('<ButtonRelease-1>', self.on_release)
        
        # Visual feedback during drag
        self.drag_line = None
        
    def on_click(self, event):
        # Get the clicked item's index
        index = self.nearest(event.y)
        if index >= 0:
            self.drag_data['item'] = self.get(index)
            self.drag_data['index'] = index
            self.drag_data['y'] = event.y
            # Select the clicked item
            self.selection_clear(0, tk.END)
            self.selection_set(index)
            
    def on_drag(self, event):
        if self.drag_data['item']:
            # Calculate new position
            new_index = self.nearest(event.y)
            if new_index >= 0:
                # Show insertion line
                self.show_drag_line(event.y)
                
    def on_release(self, event):
        if self.drag_data['item']:
            new_index = self.nearest(event.y)
            if new_index >= 0 and new_index != self.drag_data['index']:
                # Move item to new position using the app reference
                self.app.move_item(self.drag_data['index'], new_index)
            
            # Clear drag data and visual feedback
            self.drag_data = {'item': None, 'index': None, 'y': 0}
            self.remove_drag_line()
            
    def show_drag_line(self, y):
        self.remove_drag_line()
        # Create a line to show where the item will be inserted
        self.drag_line = self.create_line(y)
        
    def create_line(self, y):
        # Get the index near the current y position
        index = self.nearest(y)
        if index >= 0:
            # Get the bbox of the item at the index
            bbox = self.bbox(index)
            if bbox:
                # Determine if we should show the line above or below the item
                middle = bbox[1] + bbox[3] // 2
                y = bbox[1] if y < middle else bbox[1] + bbox[3]
                
                # Create a temporary canvas for the line
                canvas = tk.Canvas(self, height=2, width=self.winfo_width(),
                                 highlightthickness=0, bg='SystemHighlight')
                canvas.place(x=0, y=y-1)
                return canvas
        return None
        
    def remove_drag_line(self):
        if self.drag_line:
            self.drag_line.destroy()
            self.drag_line = None

class ImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image File Converter")
        self.root.geometry("650x750")  # Increased height
        self.root.minsize(650, 750)    # Set minimum window size
        
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, padding="20")
        self.main_container.pack(fill="both", expand=True)
        
        # Configure grid
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10)
        self.style.configure("TLabel", padding=5)
        
        # Create a larger font for labels
        default_font = tkfont.nametofont("TkDefaultFont")
        self.label_font = tkfont.Font(
            family=default_font.cget("family"),
            size=int(default_font.cget("size") * 1.5)  # 1.5x size for labels, convert to integer
        )
        
        self.selected_files = []
        self.setup_ui()
        
    def setup_ui(self):
        current_row = 0
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.main_container, text="File Selection", padding=10)
        file_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="No files selected", font=self.label_font)
        self.file_label.pack(side="left", fill="x", expand=True)
        
        # Button container for file selection buttons
        button_container = ttk.Frame(file_frame)
        button_container.pack(side="right")
        
        # Add Files button (initially disabled)
        self.add_files_btn = ttk.Button(button_container, text="Add Files", 
                                      command=self.add_files, state="disabled")
        self.add_files_btn.pack(side="right", padx=(5, 0))
        
        # Select Files button
        select_btn = ttk.Button(button_container, text="Select Files", 
                              command=self.select_files)
        select_btn.pack(side="right")
        
        current_row += 1
        
        # File list frame
        list_frame = ttk.LabelFrame(self.main_container, text="Selected Files (Drag to Reorder)", padding=10)
        list_frame.grid(row=current_row, column=0, sticky="nsew", padx=5, pady=5)
        self.main_container.grid_rowconfigure(current_row, weight=1)
        
        # Create list and scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(side="left", fill="both", expand=True)
        
        self.file_listbox = DraggableListbox(list_container, self, selectmode=tk.SINGLE)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Button frame
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(side="right", padx=5)
        
        remove_btn = ttk.Button(button_frame, text="Remove", command=self.remove_selected)
        remove_btn.pack(pady=2)
        
        current_row += 1
        
        # Output format frame
        format_frame = ttk.LabelFrame(self.main_container, text="Output Format", padding=10)
        format_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=5)
        
        self.output_format = tk.StringVar(value="pdf")
        formats = [("PDF", "pdf"), ("PNG", "png"), ("JPEG", "jpeg")]
        
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, value=value,
                           variable=self.output_format).pack(side="left", padx=20)
        
        current_row += 1
        
        # PDF Options frame
        self.pdf_options_frame = ttk.LabelFrame(self.main_container, text="PDF Options", padding=10)
        self.pdf_options_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=5)
        
        self.combine_pdf = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.pdf_options_frame, text="Combine images into single PDF",
                       variable=self.combine_pdf).pack(side="left", padx=5)
        
        current_row += 1
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.main_container, text="Progress", padding=10)
        progress_frame.grid(row=current_row, column=0, sticky="ew", padx=5, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill="x")
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack()
        
        current_row += 1
        
        # Convert button
        self.convert_btn = ttk.Button(self.main_container, text="Convert Files",
                                    command=self.start_conversion)
        self.convert_btn.grid(row=current_row, column=0, pady=20)
    
    def update_file_list(self):
        """Update the listbox with current files"""
        self.file_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            filename = os.path.basename(file_path)
            self.file_listbox.insert(tk.END, filename)
        
        self.file_label.config(text=f"{len(self.selected_files)} file(s) selected")
        
        # Update Add Files button state
        self.add_files_btn.configure(state="normal" if self.selected_files else "disabled")
    
    def move_item(self, old_index, new_index):
        """Move an item from old_index to new_index"""
        # Move the file in the selected_files list
        file_to_move = self.selected_files.pop(old_index)
        self.selected_files.insert(new_index, file_to_move)
        
        # Update the listbox
        self.update_file_list()
        # Maintain selection
        self.file_listbox.selection_clear(0, tk.END)
        self.file_listbox.selection_set(new_index)
    
    def remove_selected(self):
        """Remove selected item from the list"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        self.selected_files.pop(index)
        self.update_file_list()
        
        # Select next item if available
        if self.selected_files:
            next_index = min(index, len(self.selected_files) - 1)
            self.file_listbox.selection_set(next_index)
        
    def select_files(self):
        """Initial file selection that clears previous selection"""
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        if files:
            self.selected_files = list(files)
            self.update_file_list()
            # Enable the Add Files button
            self.add_files_btn.configure(state="normal")
            
    def add_files(self):
        """Add more files to existing selection"""
        files = filedialog.askopenfilenames(
            title="Add More Image Files",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        if files:
            # Add new files to the existing list
            self.selected_files.extend(files)
            self.update_file_list()
    
    def get_save_path(self, suggested_name):
        output_format = self.output_format.get()
        file_types = []
        
        if output_format == "pdf":
            file_types = [("PDF files", "*.pdf")]
        elif output_format == "png":
            file_types = [("PNG files", "*.png")]
        else:
            file_types = [("JPEG files", "*.jpeg")]
            
        file_types.append(("All files", "*.*"))
        
        return filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=f".{output_format}",
            initialfile=suggested_name,
            filetypes=file_types
        )
        
    def start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("Warning", "Please select files first!")
            return
            
        output_format = self.output_format.get()
        
        if output_format == "pdf" and self.combine_pdf.get():
            # For combined PDF, ask for single output file name
            save_path = self.get_save_path("combined_document.pdf")
            if not save_path:
                return
            output_dir = os.path.dirname(save_path)
            output_name = os.path.basename(save_path)
        else:
            # For individual files, ask for output directory
            output_dir = filedialog.askdirectory(title="Select Output Directory")
            if not output_dir:
                return
            output_name = None
            
        # Disable buttons during conversion
        self.convert_btn.state(["disabled"])
        
        # Start conversion in a separate thread
        thread = threading.Thread(target=self.convert_files, 
                                args=(output_dir, output_name))
        thread.daemon = True
        thread.start()
        
    def convert_files(self, output_dir, output_name=None):
        try:
            total_files = len(self.selected_files)
            self.progress["maximum"] = total_files
            output_format = self.output_format.get()
            
            if output_format == "pdf" and self.combine_pdf.get():
                # Combine all images into a single PDF
                self.status_label.config(text="Creating combined PDF...")
                output_path = os.path.join(output_dir, output_name)
                
                # Convert images to RGB if necessary
                images = []
                for file_path in self.selected_files:
                    with Image.open(file_path) as img:
                        if img.mode in ("RGBA", "P"):
                            rgb_img = img.convert("RGB")
                            # Save temporary file
                            temp_path = os.path.join(output_dir, f"temp_{os.path.basename(file_path)}")
                            rgb_img.save(temp_path)
                            images.append(temp_path)
                        else:
                            images.append(file_path)
                
                # Create PDF
                with open(output_path, "wb") as pdf_file:
                    pdf_file.write(img2pdf.convert(images))
                
                # Clean up temporary files
                for img_path in images:
                    if "temp_" in os.path.basename(img_path):
                        os.remove(img_path)
                
                self.progress["value"] = total_files
                
            else:
                # Process individual files
                for i, file_path in enumerate(self.selected_files, 1):
                    self.status_label.config(
                        text=f"Converting file {i} of {total_files}")
                    
                    filename = Path(file_path).stem
                    
                    if output_format == "pdf":
                        output_path = os.path.join(output_dir, f"{filename}.pdf")
                        with open(output_path, "wb") as pdf_file:
                            pdf_file.write(img2pdf.convert(file_path))
                    else:
                        output_path = os.path.join(
                            output_dir, f"{filename}.{output_format}")
                        with Image.open(file_path) as img:
                            if img.mode in ("RGBA", "P"):
                                img = img.convert("RGB")
                            img.save(output_path, format=output_format.upper())
                    
                    self.progress["value"] = i
                    self.root.update_idletasks()
            
            self.status_label.config(text="Conversion completed!")
            messagebox.showinfo("Success", "All files converted successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
        finally:
            self.convert_btn.state(["!disabled"])
            self.progress["value"] = 0
            self.status_label.config(text="Ready")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverter(root)
    root.mainloop() 