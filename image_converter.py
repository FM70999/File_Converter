import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import img2pdf
import os
from pathlib import Path
import threading

class ImageConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image File Converter")
        self.root.geometry("600x450")
        self.root.configure(padx=20, pady=20)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10)
        self.style.configure("TLabel", padding=5)
        
        self.selected_files = []
        self.setup_ui()
        
    def setup_ui(self):
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="File Selection", padding=10)
        file_frame.pack(fill="x", padx=5, pady=5)
        
        self.file_label = ttk.Label(file_frame, text="No files selected")
        self.file_label.pack(side="left", fill="x", expand=True)
        
        select_btn = ttk.Button(file_frame, text="Select Files", command=self.select_files)
        select_btn.pack(side="right")
        
        # Output format frame
        format_frame = ttk.LabelFrame(self.root, text="Output Format", padding=10)
        format_frame.pack(fill="x", padx=5, pady=5)
        
        self.output_format = tk.StringVar(value="pdf")
        formats = [("PDF", "pdf"), ("PNG", "png"), ("JPEG", "jpeg")]
        
        for text, value in formats:
            ttk.Radiobutton(format_frame, text=text, value=value,
                           variable=self.output_format).pack(side="left", padx=20)
        
        # PDF Options frame
        self.pdf_options_frame = ttk.LabelFrame(self.root, text="PDF Options", padding=10)
        self.pdf_options_frame.pack(fill="x", padx=5, pady=5)
        
        self.combine_pdf = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.pdf_options_frame, text="Combine images into single PDF",
                       variable=self.combine_pdf).pack(side="left", padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=5, pady=5)
        
        self.progress = ttk.Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill="x")
        
        self.status_label = ttk.Label(progress_frame, text="Ready")
        self.status_label.pack()
        
        # Convert button
        self.convert_btn = ttk.Button(self.root, text="Convert Files",
                                    command=self.start_conversion)
        self.convert_btn.pack(pady=20)
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        if files:
            self.selected_files = list(files)
            self.file_label.config(
                text=f"{len(files)} file(s) selected")
            
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