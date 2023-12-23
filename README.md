# PDF Orientation Corrector

## Description

The PDF Orientation Corrector is a Python module designed to automatically detect and correct the orientation of pages in a PDF file. It utilizes the PyPDF2 library for PDF manipulation, pytesseract for Optical Character Recognition (OCR) to detect text orientation, and pdf2image to convert PDF pages into images for analysis.

## Features

- Batch processing of PDF pages for efficient handling of large documents.
- Automatic detection and correction of page orientation using OCR.
- Conversion of PDF pages to images for detailed analysis.
- Simple and easy-to-use interface for both standalone execution and integration into other Python scripts.

## Requirements

To use the PDF Orientation Corrector, the following Python libraries need to be installed:

- PyPDF2
- pytesseract
- pdf2image
- concurrent.futures (standard in Python 3.2+)

## Installation

Clone this repository or download the source code. Ensure all required libraries are installed in your Python environment:

```bash
$ pip install PyPDF2 pytesseract pdf2image Pillow reportlab
```

Note: pytesseract requires a separate installation of Tesseract OCR.

## Usage

The module can be used as a standalone script or imported into other Python scripts.

### As a Standalone Script

Provide the path to the input PDF and the output file:

```bash
$ python pdf_orientation_corrector.py input.pdf output.pdf
```

### As a Module in Other Scripts

Import the module and use its functions in your scripts:

```python
import pdf_orientation_corrector

pdf_orientation_corrector.detect_and_correct_orientation('input.pdf', 'output.pdf')
```
