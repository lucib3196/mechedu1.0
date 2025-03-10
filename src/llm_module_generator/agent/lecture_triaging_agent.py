from pydantic import BaseModel,Field
from typing import List
import asyncio
import os
import json
from ..image_extraction.image_llm import ImageLLMProcessor
from langchain import hub
class Response(BaseModel):
    functions_call: List[str] = Field(...,description="An array of functions to call")
    summary: str = Field("A consise summary of the content of the content provided ")
    pages: int = Field("A number of pages/slides you were given. This is meant to indicate how much content you were given")
lecture_triaging_agent = ImageLLMProcessor(    
    prompt = hub.pull("lecture-triaging"),
    response = Response,
    model = "gpt-4o-mini"
)
lecture_triaging_agent_simple = ImageLLMProcessor(    
    prompt = hub.pull("lecture-triaging-simple"),
    response = Response,
    model = "gpt-4o-mini"
)


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
        print(result)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())