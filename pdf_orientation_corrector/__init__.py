"""
PDF Orientation Corrector Package

This package provides functionalities to automatically detect and correct 
the orientation of pages in PDF documents using Optical Character Recognition (OCR).
It is built using PyPDF2 for PDF manipulation, pytesseract for OCR, and pdf2image 
to convert PDF pages to images for analysis.

Main functionalities include converting PDF pages to images, detecting text orientation, 
applying necessary rotations, and saving the corrected PDF.
"""

from .main import detect_and_correct_orientation, preprocess_image

DEFAULT_DPI = 200
DEFAULT_BATCH_SIZE = 10
