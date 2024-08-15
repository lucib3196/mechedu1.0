import json
from typing import List, Dict, Optional
import asyncio
import os

from .send_image_request import send_image_request

async def fetch_structured_response_from_images(image_paths: List[str], prompt: str, response_format: Dict=None) -> Dict:
    """
    Sends a request with the provided images and prompt, and returns the structured response.

    Args:
        image_paths (List[str]): A list of paths to the images to be processed.
        prompt (str): The prompt to send along with the images.
        response_format (Dict): The expected format of the response.

    Returns:
        Dict: The cleaned and structured response in dictionary format.
    """
    response = await send_image_request(prompt, image_paths=image_paths, response_format=response_format)
    cleaned_response = json.loads(response["choices"][0]["message"]["content"])
    return cleaned_response

async def main(image_paths: List[str], prompt: str, response_format=None):
    """
    Main function to fetch and return the structured response from images using a given prompt.

    Args:
        image_paths (List[str]): A list of paths to the images to be processed.
        prompt (str): The prompt to send along with the images.
        response_format (Dict): The expected format of the response.

    Returns:
        Dict: The structured response obtained from the images.
    """
    result = await fetch_structured_response_from_images(image_paths, prompt, response_format)
    return result

if __name__ == "__main__":
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
        prompt = "What is in the image? Return as JSON structure."

        print("Processing the image and sending the request. Please wait...")
        result = asyncio.run(main(image_paths=image_paths, prompt=prompt))

        print("\nRequest completed successfully. Here is the result:")
        print(result)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")