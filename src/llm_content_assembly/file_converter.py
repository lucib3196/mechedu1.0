import os
import tempfile
from dataclasses import dataclass
from typing import Union, List

import fitz  # PyMuPDF

from .utils import (
    convert_pdf_to_images,
    is_image_file_extension,
    is_pdf_file_extension
)
from .temporary_directory_manager import TemporaryDirectoryManager
from ..logging_config.logging_config import get_logger


logger = get_logger(__name__)

class FileConverter:
    def __init__(self):
        self.manager = TemporaryDirectoryManager()
        self.temporary_dir = self.manager.get_tempdir()

    def convert_pdf_to_images(self,pdf_path: str):
        image_paths = []
        document = fitz.open(pdf_path)
        base_name = os.path.basename(pdf_path).replace(".pdf", "")
        logger.info("Converting PDF to Collection of Images")

        for page_number in range(document.page_count):
            filename = f"{base_name}_pg_{page_number + 1}.jpg"
            filepath = os.path.join(self.temporary_dir, filename)
            page = document.load_page(page_number)
            pix = page.get_pixmap()
            pix.save(filepath)
            image_paths.append(filepath)
            logger.info(f"Converted {filename} to image")
        return image_paths

    def convert_files_images(self, files: Union[str, List[str]]) -> List:
        # All files are images
        if isinstance(files, list) and all(is_image_file_extension(file) for file in files): 
            return files
        # A single file passed in as a string
        if isinstance(files,str) and is_image_file_extension(files):
            return [files]
        # Single PDF Path
        if isinstance(files, str) and not is_image_file_extension(files) and is_pdf_file_extension(files):
            return self.convert_pdf_to_images(files)
        # Multiple PDF Paths
        if isinstance(files, list) and all(not is_image_file_extension(file) for file in files):
            image_paths = [self.convert_pdf_to_images(file) for file in files]
            return image_paths[0]
        elif isinstance(files, list) and not all(is_image_file_extension(file) for file in files):
            return "list of mix of images and non-image files"
        return "unknown file type"
    
    def __del__(self):
        # Ensure Clean up of Temp Dir 
        self.manager.cleanup()

def main():
    # Create an instance of BatchFileConverter
    converter = FileConverter()

    # Test cases
    test_cases = [
        r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\Lecture_01_09.pdf",
        # ["image1.jpg", "image2.png", "image3.gif"],
        [r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\Lecture_01_09.pdf", r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\Lecture_01_11.pdf"],
        # ["image1.jpg", "document.pdf"],
        "unknownfile.xyz"
    ]

    # Test each case and print the result
    for files in test_cases:
        file_type = converter.convert_files_images(files)
        print(f"Input: {files}\nPaths {file_type}\n")

if __name__ == "__main__":
    main()



