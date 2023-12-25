# PDF Orientation Corrector

## Overview

The PDF Orientation Corrector is a Python module designed for automatic detection and correction of the orientation of pages in PDF documents.

## Key Features

- **Automated Page Orientation Correction**: Detects and corrects the orientation of text on each page of a PDF.
- **Batch Processing**: Enhances performance when dealing with large documents by processing pages in batches.
- **Image Preprocessing**: Uses PIL to enhance the accuracy of OCR results.

## Prerequisites

Before you begin, ensure you have met the following requirements:

Python 3.x
Libraries: PyPDF2, pytesseract, pdf2image, PIL (Pillow), concurrent.futures (part of the standard library)

## Installation

Clone the repository or download the source code. Install the required dependencies via pip:

```bash
pip install PyPDF2 pytesseract pdf2image Pillow
```

## Usage

The module can be used in two ways:

### As a Script

Run the script from the command line, providing the necessary arguments:

```bash
python pdf_orientation_corrector.py input.pdf output.pdf --batch_size 20 --dpi 300 --verbose
```

### As a Library

Import the module in your Python script:

```python
import pdf_orientation_corrector
# Use the module functions as needed
```

## Author

James Standbridge
Email: james.standbridge.git@gmail.com
