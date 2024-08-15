import asyncio 
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import os

from .fetch_response_image_extraction import fetch_structured_response_from_images

class Step(BaseModel):
    explanation: str = Field(..., description="An explanation of the step involved in solving the problem, using LaTeX for any mathematical symbols or equations.")
    output: str = Field(..., description="The output or result of the step, formatted in LaTeX if it includes any mathematical symbols or equations.")

class ImageRequirements(BaseModel):
    requires_image: str = Field(..., description="Indicates if the derivation requires an image to fully understand the derivation. Should be 'True' or 'False'.")
    recommended_image: str = Field(..., description="If the image is required, provide a recommendation of what the image should depict.")

class SingleDerivation(BaseModel):
    derivation_name: str = Field(..., description="The name of the derivation and what it aims to demonstrate.")
    derivation_steps: List[Step] = Field(..., description="A list of steps involved in the derivation, each step explained and formatted using LaTeX for mathematical symbols or equations.")
    derivation_source: str = Field(..., description="The source from which this derivation is derived.")
    image_stats: List[ImageRequirements] = Field(..., description="A list of image requirements for understanding the derivation, if any.")

class DerivationResponse(BaseModel):
    derivations: List[SingleDerivation] = Field(..., description="A list of derivations, each containing its name, steps, source, and image requirements if applicable.")


schema = DerivationResponse.model_json_schema()
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "lecture_analysis",
        "schema": schema
    }
}

async def extract_derivations_image(image_paths: List[str]) -> dict:
    """
    Extracts summary and key concepts questions from lecture images using an AI model.

    Args:
        image_paths (List[str]): A list of paths to the lecture images.

    Returns:
        dict: The structured response containing the conceptual questions.
    """
    prompt = """
        You are tasked with analyzing the following lecture slides covering a specific class topic. Please address the following points and return the results as a JSON structure with the specified keys:

        1. **Derivations**: Extract all derivations found in the lecture material. For each derivation:
            - Provide a name that describes what the derivation is trying to show.
            - Extract the full solution, including all steps as if teaching a student. Ensure to use LaTeX to render any mathematical symbols or equations, delimited by $ symbols.
            - Note that similar derivations may exist for different cases. Distinctions are often indicated by differences in images or new derivation contexts. Identify and separate these accurately.
            - Mention the completeness of each derivation. If a derivation appears incomplete, explicitly indicate this.
            - If no derivations are present, return "NaN".
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
        result = await extract_derivations_image(image_paths=image_paths)
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