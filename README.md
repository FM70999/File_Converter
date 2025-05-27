# Image File Converter

A simple and user-friendly application to convert image files to PDF and other formats, with preview and reordering capabilities.

## Features
- Convert multiple image files to PDF
- Preview images before conversion
- Drag and drop interface to reorder images
- User-friendly graphical interface with enhanced readability
- Large, easy-to-read file names and controls
- Support for common image formats (PNG, JPG, JPEG, BMP, GIF, TIFF)
- Fast conversion using efficient libraries
- Option to combine multiple images into a single PDF
- Individual file conversion support
- Progress tracking with status updates

## UI Features
- Large, readable font sizes for better visibility
- Clear file name display with enhanced text size
- Modern Windows-style selection highlighting
- Clean, uncluttered interface design
- Intuitive drag and drop reordering
- Visual feedback during drag operations

## Setup
1. Ensure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the application:
```bash
python image_converter.py
```

2. Using the application:
   - Click "Select Files" to choose your image files
   - Preview thumbnails will appear in the preview panel
   - Drag and drop thumbnails to reorder them (affects PDF page order)
   - Choose your desired output format (PDF, PNG, or JPEG)
   - For PDF conversion, you can choose to:
     * Combine all images into a single PDF (default)
     * Convert each image to a separate PDF
   - Click "Convert" to process the files
   - Select the destination folder for your converted files

## Preview Features
- Thumbnail preview of all selected images
- Drag and drop interface for reordering
- Horizontal scrolling for multiple images
- File names displayed under thumbnails
- Visual feedback during drag operations

## Requirements
- Python 3.7+
- Pillow (PIL)
- img2pdf
- tkinter (usually comes with Python)

## Supported Formats
### Input Formats:
- PNG
- JPEG/JPG
- BMP
- GIF
- TIFF

### Output Formats:
- PDF (single or multiple files)
- PNG
- JPEG 