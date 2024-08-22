import asyncio
import os
import io
import zipfile
import logging
import tempfile
from time import time
from io import BytesIO
from typing import Union, List, Dict, Any
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from PIL import Image

from ..llm_generators.image_extraction.extract_computational_questions import computational_question_extraction_images

# Configure logging
logging.basicConfig(level=logging.INFO)


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

def convert_pdf_to_images(pdf_path: str, tempdir: str) -> List[str]:
    image_paths = []

    document = fitz.open(pdf_path)
    base_name = os.path.basename(pdf_path).replace(".pdf", "")
    logging.info("Converting PDF to Collection of Images")
    
    for page_number in range(document.page_count):
        filename = f"{base_name}_pg_{page_number + 1}.jpg"
        filepath = os.path.join(tempdir, filename)
        page = document.load_page(page_number)
        pix = page.get_pixmap()
        pix.save(filepath)
        image_paths.append(filepath)
        logging.info(f"Converted {filename} to image")

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
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("jpg")  # Convert pixmap to JPEG bytes
        image_data = BytesIO(img_bytes)  # Store the image in a BytesIO object
        image_data_list.append(image_data)

    return image_data_list

def create_zip_file(file_paths: List[str], base_dir: str) -> BytesIO:
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.relpath(file_path, base_dir))
    memory_file.seek(0)
    return memory_file

# Main entry point
async def main():
    pass

if __name__ == "__main__":
    asyncio.run(main())
