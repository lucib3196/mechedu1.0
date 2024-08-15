import asyncio
import base64
from typing import List

async def encode_image(image_path: str) -> str:
    """
    Encodes an image to a base64 string.

    Args:
        image_path (str): The file path of the image to encode.

    Returns:
        str: The base64 encoded string of the image.

    Raises:
        Exception: If an error occurs while reading or encoding the image.
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        raise

async def encode_multiple_images(image_paths: List[str], debug: bool = False) -> List[str]:
    """
    Encodes multiple images to base64 strings asynchronously.

    Args:
        image_paths (List[str]): A list of file paths for the images to encode.
        debug (bool, optional): If True, prints the results as they are received. Defaults to False.

    Returns:
        List[str]: A list of base64 encoded strings corresponding to the input images.
    """
    results = await asyncio.gather(*(encode_image(image_path) for image_path in image_paths))
    
    if debug:
        for result in results:
            print(f"Received Result: {result}")
    
    return results
