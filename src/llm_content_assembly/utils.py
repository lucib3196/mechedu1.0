
import os
import logging
from time import time
from io import BytesIO
from typing import Union, List, Dict, Any
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from ..logging_config.logging_config import get_logger
logger = get_logger(__name__)
# Utility functions

def is_adaptive_question(metadata_dict: dict) -> bool:
    if not isinstance(metadata_dict, dict):
        raise TypeError(f"Expected a dictionary, but got {type(metadata_dict).__name__} instead.")
    
    if "isAdaptive" not in metadata_dict:
        raise KeyError("Key 'isAdaptive' not found in the dictionary.")
    
    return metadata_dict["isAdaptive"]

def extract_question_title(metadata_dict: dict) -> str:
    if "title" not in metadata_dict:
        raise KeyError("Key 'title' not found in the dictionary.")
    return metadata_dict.get("title", "Undefined Title")

def is_image_file_extension(file_path: str) -> bool:
    return file_path.endswith(('.png', '.jpg', '.jpeg'))
def is_pdf_file_extension(file_path: str) -> bool:
    return file_path.endswith(('.pdf'))

def convert_pdf_to_images(pdf_path: str, tempdir: str) -> List[str]:
    image_paths = []

    document = fitz.open(pdf_path)
    base_name = os.path.basename(pdf_path).replace(".pdf", "")
    logger.info("Converting PDF to Collection of Images")
    
    for page_number in range(document.page_count):
        filename = f"{base_name}_pg_{page_number + 1}.jpg"
        filepath = os.path.join(tempdir, filename)
        page = document.load_page(page_number)
        pix = page.get_pixmap() # type: ignore
        pix.save(filepath)
        image_paths.append(filepath)
        logger.info(f"Converted {filename} to image")
    return image_paths

def convert_pdf_to_images_in_memory(pdf_path: str) -> List[BytesIO]:
    """
    Converts each page of a PDF file to an image and returns the images as in-memory BytesIO objects.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        List[BytesIO]: A list of BytesIO objects containing the image data.
    """
    image_data_list = []

    document = fitz.open(pdf_path)
    for page_number in range(document.page_count):
        page = document.load_page(page_number)
        pix = page.get_pixmap() # type: ignore
        img_bytes = pix.tobytes("jpg")  # Convert pixmap to JPEG bytes
        image_data = BytesIO(img_bytes)  # Store the image in a BytesIO object
        image_data_list.append(image_data)

    return image_data_list

