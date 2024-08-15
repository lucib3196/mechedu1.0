from ..image_extraction.send_image_request import send_image_request
from pydantic import BaseModel,Field
from typing import List
import asyncio
import os
import json
triaging_system_prompt = """
You are responsible for assessing the user's query and analyzing the provided material. Route the query to the appropriate functions based on the content. The available functions are:

- **extract_summary_and_key_concepts**: Use this function to extract the summary and key concepts only if the material is long and formatted as a lecture. This function is not applicable for short materials or collections of questions.

- **conceptual_question_extraction**: This function must always be called if extract_summary_and_key_concepts is used, as it complements the extraction of key concepts by generating or extracting related conceptual questions. For shorter materials, such as a collection of questions, this function should follow the same conditions as the extract_computational_questions function.

- **extract_derivations**: Extract mathematical derivations only if it is clear that the material contains formal mathematical derivations. 

- **computational_question_extraction**: This function extracts computational questions along with their solution.This function is ideally used when the material includes problems with solutions. This function works for single to multiple questions present
Forward the user's query to the relevant functions using the send_query_to_functions tool based on the material's content and format.
"""
class Response(BaseModel):
    functions_call: List[str] = Field(...,description="An array of functions to call")

schema = Response.model_json_schema()
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "lecture_analysis",
        "schema": schema
    }
}

async def lecture_triaging_agent(image_paths: list[str]):
    responses = await send_image_request(prompt = triaging_system_prompt,response_format=response_format, image_paths=image_paths)
    cleaned_response = json.loads(responses["choices"][0]["message"]["content"])
    return cleaned_response.get("functions_call",[])

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
        result = await lecture_triaging_agent(image_paths=image_paths)
        print(result)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

if __name__ == "__main__":
    asyncio.run(main())