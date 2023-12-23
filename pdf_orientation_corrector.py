"""
PDF Orientation Corrector

This module provides functionalities to detect and correct the 
orientation of pages in a PDF file. It uses a combination of PyPDF2 for PDF manipulation, pytesseract for OCR (Optical Character Recognition) to detect text orientation, and pdf2image to convert PDF pages to images for analysis.

The module processes PDF files in batches, which enhances performance 
when dealing with large documents. It can be used as a standalone script
or imported into other Python scripts for PDF processing.

Author: James Standbridge
Email: james.standbridge.git@gmail.com

Requirements:
    - PyPDF2
    - pytesseract
    - pdf2image
    - PIL
    - concurrent.futures
    - reportlab

Usage:
    To use this module as a script, provide the path to the input PDF 
    file and the desired output file path. 

    Example:
        python pdf_orientation_corrector.py input.pdf output.pdf

Functions:
    - convert_page_to_image: Converts a specific page of a PDF to an image.
    - extract_rotation_angle: Extracts the necessary rotation angle for an image.
    - process_pages_in_batch: Processes a batch of pages to determine their rotation.
    - detect_and_correct_orientation: Detects and corrects the orientation of each page 
      in a PDF file.
    - is_upside_down: Determines if an image is upside down based on its rotation angle.
"""


from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pytesseract
import re
from pdf2image import convert_from_path
from tempfile import NamedTemporaryFile
import concurrent.futures

def convert_page_to_image(pdf_path, page_num=0, dpi=200):
    """
    Converts a specific page of a PDF file into an image.

    Args:
    pdf_path (str): Path to the PDF file.
    page_num (int): Page number to be converted (starts from 0).
    dpi (int): Resolution of the image in DPI.

    Returns:
    PIL.Image: An image object representing the converted page.
    """
    images = convert_from_path(pdf_path, dpi=dpi, first_page=page_num + 1, last_page=page_num + 1)
    return images[0]

def extract_rotation_angle(image):
    """
    Extracts the necessary rotation angle for an image using pytesseract.

    Args:
    image (PIL.Image): Image object for which to determine the rotation.

    Returns:
    tuple: A tuple containing the rotation angle and the orientation in degrees.
    """
    osd = pytesseract.image_to_osd(image)
    rotation_angle = int(re.search('Rotate: (\d+)', osd).group(1))
    orientation = re.search('Orientation in degrees: (\d+)', osd).group(1)

    return rotation_angle, int(orientation)

def process_pages_in_batch(pdf_path, page_nums, batch_size=10):
    """
    Processes a batch of pages to determine their required rotation.

    Args:
    pdf_path (str): Path to the PDF file.
    page_nums (list): List of page numbers to process.
    batch_size (int): Number of pages in each batch.

    Returns:
    list: List of tuples (page number, rotation).
    """
    results = []
    for page_num in page_nums:
        image = convert_page_to_image(pdf_path, page_num)
        rotation_angle, orientation = extract_rotation_angle(image)
        rotation = None
        if orientation == 90:
            rotation = -90
        elif orientation == 270:
            rotation = 90
        elif is_upside_down(rotation_angle):
            rotation = 180

        results.append((page_num, rotation))
    return results

def detect_and_correct_orientation(pdf_path, output_path, batch_size=10):
    """
    Detects and corrects the orientation of each page in a PDF file.

    Args:
    pdf_path (str): Path to the PDF file to be processed.
    output_path (str): Path for the output PDF file with corrected orientation.
    batch_size (int): Number of pages to process in each batch.
    """
    reader = PdfReader(pdf_path)
    page_nums = range(len(reader.pages))
    batches = [page_nums[i:i + batch_size] for i in range(0, len(page_nums), batch_size)]

    all_rotations = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_pages_in_batch, pdf_path, batch) for batch in batches]
        for future in concurrent.futures.as_completed(futures):
            all_rotations.extend(future.result())

    all_rotations.sort(key=lambda x: x[0])

    writer = PdfWriter()
    for page_num, rotation in all_rotations:
        page = reader.pages[page_num]
        if rotation is not None:
            page.rotate(rotation)
        writer.add_page(page)

    with open(output_path, 'wb') as out_pdf:
        writer.write(out_pdf)

def is_upside_down(rotation_angle):
    """
    Determines if an image is upside down based on its rotation angle.

    Args:
    rotation_angle (int): Angle of rotation in degrees.

    Returns:
    bool: True if the image is upside down, False otherwise.
    """
    return abs(rotation_angle - 180) < 45

if __name__ == "__main__":
    detect_and_correct_orientation('test_2-rotated.pdf', 'fixed_rotation.pdf')