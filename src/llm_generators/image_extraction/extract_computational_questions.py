import asyncio 
from typing import List, Dict, Optional, Union,Tuple
from pydantic import BaseModel, Field
import os

from .fetch_response_image_extraction import fetch_structured_response_from_images
class Step(BaseModel):
    explanation: str = Field(..., description="An explanation of the step involved in solving the problem, using LaTeX for any mathematical symbols or equations.")
    output: str = Field(..., description="The output or result of the step, formatted in LaTeX if it includes any mathematical symbols or equations. Should not contain numerical numbers instead it should be formatted symbolically")

class ImageReq(BaseModel):
    requires_image: bool = Field(...,description="Indicate wether the question requires an image to solve")
    image_description: Optional[str] = Field(...,description="If the question requires an image to solve, provide a description of the image that is needed.")

class ExternalDataReq(BaseModel):
    requires_external_data: bool = Field(...,description="Indicates whether external data, such as tabular data or charts, is needed to solve the question.")
    external_data: Optional[str] = Field(...,description="If external data is required indicate the required data")

class ComputationalQuestion(BaseModel):
    question: str = Field(..., description="A computational question that requires computation. Format any mathematical symbols or equations using LaTeX.")
    solution: Optional[List[Step]] = Field(None, description="A detailed solution with steps for the computational question, using LaTeX for formatting any mathematical symbols or equations. This field is optional and should be `None` if a solution is not present, particularly if the `complete` field is `false`.")
    source: str = Field(..., description="The source from which this question is derived.")
    complete: bool = Field(..., description="Indicates if the computational question is completed with the solutions. If `false`, the `solution` field can be `None`.")
    image_req: ImageReq
    external_data_req: ExternalDataReq
    
class ExtractedCompuationalQuestions(BaseModel):
    extracted_question: List[ComputationalQuestion]
    
# Define the JSON schema for the response format
schema = ExtractedCompuationalQuestions.model_json_schema()
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "lecture_analysis",
        "schema": schema
    }
}

# print(response_format)

async def computational_question_extraction_images(image_paths: List[str]) -> dict:
    """
    Extracts conceptual questions from lecture images using an AI model.

    Args:
        image_paths (List[str]): A list of paths to the lecture images.

    Returns:
        dict: The structured response containing the conceptual questions.
    """
    prompt = """
    Extract and process the content from the provided image according to these guidelines:

    1. **Extract the Question**:
    - Extract the question from the image or lecture. Ensure that all necessary details, data, and parameters are included to fully understand the question.
    - Represent any special characters, such as mathematical symbols, in LaTeX format.

    2. **Develop the Solution Guide**:
    - Analyze the image and create a concise solution guide that outlines the methodical steps for solving the problem symbolically.
    - Focus on symbolic representation rather than numerical values.
    - Include relevant conversion factors and generalize the solution for both SI and USCS units where applicable.
    - Structure the solution guide as follows:
        - **Problem Statement**: Clearly define the objective and context of the problem as shown in the image.
        - **Variables Description**: Describe all variables discernible from the image, using LaTeX for any mathematical expressions.
        - **Equation Setup**: Identify and set up the equations or relationships shown or implied in the image, using LaTeX for mathematical representations.
        - **Solution Process**: Detail each step of the solution process, using LaTeX for all mathematical workings.
        - **Explanation and Clarification**: Provide thorough explanations and clarifications based on the content of the image, with all mathematical justifications in LaTeX.
        - **Symbolic Representation Only**: The solution guide should only include symbolic representations, avoiding any numerical values.
        - **Generalization for SI and USCS**: Generalize the solution for both SI and USCS units, including relevant conversion factors for both systems.

    Ensure the extracted content adheres strictly to these guidelines, emphasizing clarity, accuracy, and completeness in both the question and the solution guide.
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
        result = await computational_question_extraction_images(image_paths=image_paths)
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