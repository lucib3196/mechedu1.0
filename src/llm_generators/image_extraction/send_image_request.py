import aiohttp
from typing import List, Optional, Union
from .utils import encode_multiple_images
from ...credentials import api_key

async def create_image_content_payload(image_paths: List[str]) -> List[dict]:
    """
    Encodes images to base64 and creates a content payload for each image.

    Args:
        image_paths (List[str]): A list of file paths for the images to encode.

    Returns:
        List[dict]: A list of dictionaries, each representing an image content payload.
    """
    images = await encode_multiple_images(image_paths)
    image_contents = [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{image}",
                "detail": "high"
            }
        }
        for image in images
    ]
    return image_contents

async def create_payload(
    prompt: str, 
    image_contents: Optional[List[dict]], 
    max_tokens: int = 5000, 
    response_format: Optional[str] = None, 
    tools: Optional[str] = None, 
    model: str = "gpt-4o-2024-08-06"
) -> Union[dict, str]:
    """
    Creates the payload for the API request based on the given parameters.

    Args:
        prompt (str): The text prompt to send to the model.
        image_contents (Optional[List[dict]]): The image content payload, if any.
        max_tokens (int): The maximum number of tokens to generate. Defaults to 5000.
        response_format (Optional[str]): The desired format of the response. Defaults to None.
        tools (Optional[str]): The tools to be used in the generation process. Defaults to None.
        model (str): The model to use. Defaults to "gpt-4o-2024-08-06".

    Returns:
        Union[dict, str]: The payload dictionary or an error string if both tools and response_format are provided.
    """
    if tools and response_format:
        return "Error: Can only have one or the other"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": (
                    {"type": "text", "text": prompt} if image_contents is None else
                    [
                        {"type": "text", "text": prompt},
                        *image_contents
                    ]
                )
            }
        ],
        "temperature": 0,
        "max_tokens": max_tokens
    }

    if tools:
        payload["tools"] = tools
    else:
        if response_format:
            payload["response_format"] = response_format
        else:
            payload["response_format"] = {"type": "json_object"}

    return payload

async def send_image_request(
    prompt: str,
    image_paths: List[str],
    api_key: str = api_key,
    max_tokens: int = 5000,
    response_format: Optional[str] = None,
    tools: Optional[str] = None
) -> dict:
    """
    Sends an asynchronous request to the API with the given prompt and images.

    Args:
        prompt (str): The text prompt to send to the model.
        image_paths (List[str]): A list of file paths for the images to encode and send.
        api_key (str): The API key for authentication.
        max_tokens (int): The maximum number of tokens to generate. Defaults to 5000.
        response_format (Optional[str]): The desired format of the response. Defaults to None.
        tools (Optional[str]): The tools to be used in the generation process. Defaults to None.

    Returns:
        dict: The API response as a dictionary.

    Raises:
        Exception: If the request fails or the response status is not 200.
    """
    image_contents = await create_image_content_payload(image_paths)

    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = await create_payload(prompt, image_contents, max_tokens, response_format, tools)

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=header,
            json=payload
        ) as response:
            response_text = await response.text()

            if response.status != 200:
                raise Exception(f"Request failed with status {response.status}: {response_text}")

            data = await response.json()

    return data
