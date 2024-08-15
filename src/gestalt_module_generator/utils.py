from typing import Union, List, Dict, Any
from time import time
import asyncio
import json
import os
import io
import zipfile

from ..llm_generators.image_extraction.extract_computational_questions import computational_question_extraction_images


async def handle_image_inputs(user_input: List[str]) -> List[Dict]:
    """
    Processes a list of user inputs (image paths) and extracts computational questions and their solutions.

    Args:
        user_input (List[str]): List of paths to user input images.

    Returns:
        Dict[str, Any]: A dictionary where each key is a question and the value is the corresponding solution.
    """
    result = await computational_question_extraction_images(user_input)
    extracted_questions = result.get("extracted_question", [])
    
    collection = []

    if extracted_questions:
        for extracted_question in extracted_questions:
            print(f"This is the extracted data {extracted_question}\n")
            question = extracted_question.get("question", "")
            if question:
                print(f"Processing question: {question}\n")
                
                is_complete = extracted_question.get("complete", False)
                if is_complete:
                    solution = extracted_question.get("solution", [])
                    solution_guide = ""
                    
                    for step in solution:
                        explanation = step.get('explanation', 'No explanation provided')
                        output = step.get('output', 'No output provided')
                        solution_guide += f"\n{explanation}\n{output}"

                    question_mapping = {
                        "question":question,
                        "solution": solution_guide,
                        "image_req": extracted_question.get("image_req", ""),
                        "external_data_req": extracted_question.get("external_data_req", "")
                    }
                    collection.append(question_mapping)
                else:
                    print(f"Question '{question}' is incomplete or missing solutions.")
            else:
                print("No question found in the extracted data.")

    return collection

async def main():
    try:
        print("Please enter the absolute path to the image file:")
        image_path = input()
        # Validate the provided path
        if not os.path.isabs(image_path):
            raise ValueError("The provided path is not an absolute path.")
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"No file found at {image_path}. Please provide a valid image file path.")
        image_paths = [f"{image_path}"]
        print(image_paths)
        print("Processing the image and sending the request. Please wait...")
        result = await handle_image_inputs(user_input=image_paths)
        print("\nRequest completed successfully. Here is the result:")
        print(result)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

def create_zip_file(file_paths, base_dir):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.relpath(file_path, base_dir))
    memory_file.seek(0)
    return memory_file



if __name__ == "__main__":
    asyncio.run(main())