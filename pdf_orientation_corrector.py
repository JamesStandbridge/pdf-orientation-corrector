"""
PDF Orientation Corrector

This Python module is designed to automatically detect and correct the orientation of pages 
in a PDF document. It leverages the combined capabilities of several libraries, including 
PyPDF2 for PDF manipulation, pytesseract for Optical Character Recognition (OCR) to detect 
text orientation, and pdf2image to convert PDF pages into images suitable for analysis. 
Additional image processing is performed using PIL to enhance OCR accuracy.

The module is optimized for processing large documents in batches, improving performance 
and efficiency. It can be utilized both as a standalone script and integrated into other 
Python scripts or applications for automated PDF processing.

Key Features:
- Converts PDF pages to images for text orientation analysis.
- Uses OCR to detect the text orientation and determine the necessary rotation for correction.
- Processes documents in batches for optimized performance.
- Applies image preprocessing techniques to improve OCR accuracy.
- Corrects the orientation of each page and generates a new PDF file with adjusted pages.

Requirements:
- PyPDF2
- pytesseract
- pdf2image
- PIL (Pillow)
- concurrent.futures (standard library)

Usage:
Run the module as a script providing the path to the input PDF file and the desired output 
file path. Optional parameters include batch size and DPI for image conversion. Verbose 
logging can be enabled for detailed process information.

Example Command:
    python pdf_orientation_corrector.py input.pdf output.pdf --batch_size 20 --dpi 300 --verbose

As a library, import the module and use its functions in other scripts to correct the 
orientation of PDF pages.

Author: 
James Standbridge (james.standbridge.git@gmail.com)

This module is part of a larger project aimed at document processing and automation, 
developed with the goal of streamlining the handling of PDF documents in various 
business and academic contexts.

"""


from PyPDF2 import PdfReader, PdfWriter
import pytesseract
import re
from pdf2image import convert_from_path
import concurrent.futures
from PIL import ImageFilter, ImageEnhance
import argparse


def preprocess_image(image):
    """
    Applies preprocessing to a PDF page image to enhance text visibility. 
    This includes converting to grayscale, enhancing contrast, applying a median filter, 
    and thresholding.

    Args:
        image (PIL.Image): The image to preprocess.

    Returns:
        PIL.Image: The preprocessed image.
    """

    image = image.convert('L')

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)

    image = image.filter(ImageFilter.MedianFilter())

    threshold = 120
    image = image.point(lambda p: p > threshold and 255)

    return image

def convert_page_to_image(pdf_path, page_num=0, dpi=200):
    """
    Converts a specific page of a PDF file into an image. 
    Applies preprocessing to improve OCR results.

    Args:
        pdf_path (str): Path to the PDF file.
        page_num (int): Page number to convert, starting from 0.
        dpi (int): Resolution of the image in DPI.

    Returns:
        PIL.Image: An image object representing the converted and preprocessed page, 
                   or None if an error occurs.
    """

    if(VERBOSE_LOGGING):
        print(f"Converting page {page_num} to image...")

    try:
        images = convert_from_path(
            pdf_path, dpi=dpi, 
            first_page=page_num + 1, 
            last_page=page_num + 1
        )
        preprocessed_image = preprocess_image(images[0])
        return preprocessed_image
    except Exception as e:
        print(f"Error while converting page to image : {e}")
        return None


def extract_rotation_angle(image):
    """
    Extracts the rotation angle of the text in an image using OCR (Optical Character Recognition).

    Args:
        image (PIL.Image): Image object to analyze.

    Returns:
        tuple: A tuple containing the rotation angle and the text orientation in degrees.
    """
    osd = pytesseract.image_to_osd(image)
    rotation_angle = int(re.search('Rotate: (\d+)', osd).group(1))
    orientation = re.search('Orientation in degrees: (\d+)', osd).group(1)

    if(VERBOSE_LOGGING):
        print(f"Rotation angle detected: {rotation_angle} degrees")
        print(f"Orientation in degrees: {orientation}")

    return rotation_angle, int(orientation)


def process_pages_in_batch(pdf_path, page_nums, dpi=300, batch_size=10):
    """
    Processes a batch of pages from a PDF to determine their required rotation angles.

    Args:
        pdf_path (str): Path to the PDF file.
        page_nums (list): List of page numbers to process.
        dpi (int): DPI setting for image conversion.
        batch_size (int): The number of pages to process in each batch.

    Returns:
        list: A list of tuples containing page numbers and their required rotations.
    """

    results = []
    for page_num in page_nums:
        if(VERBOSE_LOGGING):
            print(f"Processing page {page_num}...")
        image = convert_page_to_image(pdf_path, page_num, dpi)
        rotation_angle, orientation = extract_rotation_angle(image)
        rotation = None
        if orientation == 90:
            rotation = -90
            if(VERBOSE_LOGGING):
                print(f"Page {page_num} needs -90 degrees rotation.")
        elif orientation == 270:
            rotation = 90
            if(VERBOSE_LOGGING):
                print(f"Page {page_num} needs 90 degrees rotation.")
        elif is_upside_down(rotation_angle):
            rotation = 180
            if(VERBOSE_LOGGING):
                print(f"Page {page_num} is upside down. Needs 180 degrees rotation.")

        results.append((page_num, rotation))
    return results

def detect_and_correct_orientation(pdf_path, output_path, batch_size=10, dpi=300):
    """
    Detects and corrects the orientation of each page in a PDF file.

    Args:
        pdf_path (str): Path to the PDF file to be processed.
        output_path (str): Path for the output PDF file with corrected orientation.
        batch_size (int): Number of pages to process in each batch.
        dpi (int): DPI setting for image conversion.

    Returns:
        None: This function saves the corrected PDF to the specified output path.
    """

    if(VERBOSE_LOGGING):
        print("Starting orientation correction process...")

    reader = PdfReader(pdf_path)
    page_nums = range(len(reader.pages))
    batches = [page_nums[i:i + batch_size] for i in range(0, len(page_nums), batch_size)]

    all_rotations = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_pages_in_batch, pdf_path, batch, dpi) for batch in batches]
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
    
    if(VERBOSE_LOGGING):
        print("Orientation correction completed. Output saved to", output_path)


def is_upside_down(rotation_angle):
    """
    Determines if an image is upside down based on its rotation angle.

    Args:
        rotation_angle (int): The rotation angle of the image in degrees.

    Returns:
        bool: True if the image is upside down, False otherwise.
    """
        
    return abs(rotation_angle - 180) < 45

def set_verbose_logging(enable):
    """
    Enables or disables verbose logging globally for the module.

    Args:
        enable (bool): True to enable verbose logging, False to disable it.

    Returns:
        None
    """

    global VERBOSE_LOGGING
    VERBOSE_LOGGING = enable


VERBOSE_LOGGING = True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Orientation Corrector")

    parser.add_argument("input_file", help="Path to the input PDF file")
    parser.add_argument("output_file", help="Path for the output PDF file")
    parser.add_argument("--batch_size", type=int, default=10, help="Number of pages to process in each batch")
    parser.add_argument("--dpi", type=int, default=200, help="DPI setting for image conversion")
    parser.add_argument("--verbose", action='store_true', help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        set_verbose_logging(True)
    else:
        set_verbose_logging(False)

    try:
        detect_and_correct_orientation(args.input_file, args.output_file, args.batch_size, args.dpi)
    except FileNotFoundError:
        print("Erreur : Couldn't found specified PDF file.")
    except Exception as e:
        print(f"Unexpected error : {e}")

