import asyncio 
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import os
from .fetch_response_image_extraction import fetch_structured_response_from_images

class LectureSummary(BaseModel):
    summary: str = Field(..., description="A summary of the lecture material, describing the essence of what the lecture was about. Use LaTeX for any mathematical symbols or equations.")
    key_concepts: List[str] = Field(..., description="A list of key concepts covered in the lecture. Use LaTeX for any mathematical symbols or equations.")
    keywords: List[str] = Field(..., description="A list of keywords that describe the lecture. Use LaTeX for any mathematical symbols or equations.")
    foundational_concepts: List[str] = Field(..., description="A list of prerequisite concepts that the lecture builds upon. Use LaTeX for any mathematical symbols or equations.")

class LectureAnalysis(BaseModel):
    analysis: LectureSummary = Field(..., description="The analysis of the lecture material.")

schema = LectureAnalysis.model_json_schema()
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "lecture_analysis",
        "schema": schema
    }
}

async def extract_summary_and_key_concepts_image(image_paths: List[str]) -> dict:
    """
    Extracts summary and key concepts questions from lecture images using an AI model.

    Args:
        image_paths (List[str]): A list of paths to the lecture images.

    Returns:
        dict: The structured response containing the conceptual questions.
    """
    prompt = """
    You are tasked with analyzing the following lecture slides covering a specific class topic. Please address the following questions and return the results as a JSON structure with the specified keys:

    1. **summary**: Provide a comprehensive summary of the lecture material.
    2. **key_concepts**: Identify and explain the key concepts presented in the lecture. Provide a summary of each concept and any relevant background information. If the content requires a math equation, use LaTeX to render the equation and delimit using $.
    3. **keywords**: Describe the lecture content using relevant keywords.
    4. **foundational_concepts**: Determine and outline the foundational concepts that the lecture builds upon.
    """

    response = await fetch_structured_response_from_images(image_paths, prompt, response_format)
    return response

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
        result = await extract_summary_and_key_concepts_image(image_paths=image_paths)
        print("\nRequest completed successfully. Here is the result:")
        print(result)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

if __name__ == "__main__":
    asyncio.run(main())