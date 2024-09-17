import asyncio
import os
import json
from typing import List, Dict
from dataclasses import dataclass, field
from .send_image_request import send_image_request

@dataclass
class ImageToLLMProcessor:
    """
    A class responsible for processing images and interacting with an LLM.

    Attributes
        total_tokens (int): The total number of tokens used in LLM responses.
    """
    prompt:str 
    response_schema:str 
    total_tokens: int = field(default=0, init=False)
    
    def __post_init__(self):
        self.response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": "image_extraction",
            "schema": self.response_schema
        }}

    async def send_request(self, image_paths: List[str]) -> Dict:
        """
        Sends a request to the LLM with the provided images and prompt.

        Args:
            image_paths (List[str]): A list of paths to the images to be processed.
            prompt (str): The prompt to send along with the images.
            response_format (Dict): The expected format of the response (optional).

        Returns:
            Dict: The structured response obtained from the images.
        """
        response = await send_image_request(prompt=self.prompt, image_paths=image_paths,response_format=self.response_format)
        self.total_tokens += int(response["usage"]["total_tokens"])
        print(f"total tokens {self.total_tokens}")
        return json.loads(response["choices"][0]["message"]["content"])

    def get_total_tokens(self) -> int:
        """
        Returns the total number of tokens used in LLM responses.

        Returns:
            int: The total number of tokens.
        """
        return self.total_tokens


async def main(image_paths: List[str], prompt: str, response_format: Dict = None) -> tuple[dict,int]:
    """
    Main function to fetch and return the structured response from images using a given prompt.

    Args:
        image_paths (List[str]): A list of paths to the images to be processed.
        prompt (str): The prompt to send along with the images.
        response_format (Dict): The expected format of the response (optional).

    Returns:
        Dict: The structured response obtained from the images.
    """
    image_processor = ImageToLLMProcessor()

    result = await image_processor.send_request(prompt=prompt, image_paths=image_paths, response_format=response_format)
    total_token: int = image_processor.get_total_tokens()
    return result, total_token


if __name__ == "__main__":
    try:
        print("Please enter the absolute path to the image file:")
        image_path = input().strip()

        # Validate the provided path
        if not os.path.isabs(image_path):
            raise ValueError("The provided path is not an absolute path.")
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"No file found at {image_path}. Please provide a valid image file path.")

        image_paths = [image_path]
        prompt = "Extract all the questions. Return as JSON structure."

        print("Processing the image and sending the request. Please wait...")
        result, token_count = asyncio.run(main(image_paths=image_paths, prompt=prompt))

        print("\nRequest completed successfully. Here is the result:")
        print(result)
        print(f"Total tokens used: {token_count}")

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
