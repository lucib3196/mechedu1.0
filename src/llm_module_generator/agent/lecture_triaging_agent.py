from ..image_extraction.send_image_request import send_image_request
from pydantic import BaseModel,Field
from typing import List
import asyncio
import os
import json
from ..image_extraction.image_llm_processor import ImageToLLMProcessor


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

agent_schema = Response.model_json_schema()


lecture_triaging_agent = ImageToLLMProcessor(triaging_system_prompt,agent_schema)


async def main():
    try:
        print("Please enter the absolute paths to the image files, separated by commas:")
        image_paths_input = input()
        
        # Split the input into a list of paths
        image_paths = [path.strip() for path in image_paths_input.split(',')]
        
        # Validate each provided path
        for image_path in image_paths:
            if not os.path.isabs(image_path):
                raise ValueError(f"The provided path '{image_path}' is not an absolute path.")
            if not os.path.isfile(image_path):
                raise FileNotFoundError(f"No file found at '{image_path}'. Please provide a valid image file path.")
        
        print(image_paths)
        print("Processing the images and sending the request. Please wait...")
        
        # Process the images using the lecture_triaging_agent
        result = await lecture_triaging_agent.send_request(image_paths)
        total_tokens = lecture_triaging_agent.get_total_tokens()
        
        print(result)
        print(f"Total tokens used: {total_tokens}")

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())