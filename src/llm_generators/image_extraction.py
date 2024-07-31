import base64
import requests
from src.utils.string_parser import extract_triple_quotes
from credentials import api_key
from pydantic.main import BaseModel
from src.llm_generators.llm_templates import extract_question_image_template,extract_solution_image_tempate, code_guide_template
import logging
import aiohttp
import asyncio



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        raise
    
async def encode_image_and_send_request(prompt: str, image_paths: list, api_key: str=api_key, max_tokens: int = 2000):
    try:
        image_contents = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{await encode_image(image_path)}", "detail": "high"}} for image_path in image_paths]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *image_contents
                    ]
                }
            ],
            "temperature": 0,
            "max_tokens": max_tokens
        }

        # Print the payload and headers for debugging
        # print("Headers:", headers)
        # print("Payload:", payload)

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                # print("Response status:", response.status)  # Debugging information
                response_text = await response.text()
                # print("Response text:", response_text)  # Debugging information
                if response.status != 200:
                    raise Exception(f"Request failed with status {response.status}")
                data = await response.json()

        if 'choices' in data and data['choices']:
            content = data['choices'][0]['message']['content']
            tokens = data.get("usage", {})
            # print("This is the content", content)
            if not content:
                raise Exception("Extracted content is empty.")
            return content
        else:
            raise Exception("No choices found in data.")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


async def extract_question_image(image_paths):
    prompt = extract_question_image_template
    result = await encode_image_and_send_request(prompt, image_paths=image_paths)
    return result

async def extract_solution(image_paths):
    prompt = extract_solution_image_tempate
    result = await encode_image_and_send_request(prompt, image_paths=image_paths)
    return result

async def code_guide_image(image_paths):
    prompt = code_guide_template
    result = await encode_image_and_send_request(prompt, image_paths=image_paths)
    return result
    
    
    