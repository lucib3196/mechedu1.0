from ..image_extraction.extract_derivations_images import extract_derivations_image
from .generate_ui import generate_and_return_ui
from .generate_html_from_ui import ui_to_html
import asyncio
import os
import json
from typing import List
from bs4 import BeautifulSoup
import os
import asyncio


def extract_multiple_derivations(response: dict) -> List[str]:
    derivations = response.get("derivations", [])
    all_derivations = [
        f"Derivation Name: {derivation.get('derivation_name', 'Unknown')}" +
        "".join(
            f"\n - Explanation: {step.get('explanation', 'No explanation provided')}"
            f"\n - Step: {step.get('output', 'No output provided')}"
            for step in derivation.get("derivation_steps", [])
        )
        for derivation in derivations
    ]
    return all_derivations

def create_multiple_prompts(base_prompt: str, response: dict) -> List[str]:
    derivations = extract_multiple_derivations(response)
    return [base_prompt + derivation for derivation in derivations]

async def generate_derivations_html(response: dict) -> BeautifulSoup:
    base_prompt = """
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate.
    You are only focused on working on the following sections. When you need to format any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters to ensure proper rendering.

    **Instructions:**

    1. **Derivations**: Present any mathematical derivations or logical arguments discussed in the lecture. This section should be meticulously formatted to showcase each step clearly, allowing readers to follow the derivation process step by step. Utilize appropriate HTML tags for mathematical notation and consider using ordered lists or numbered headings to denote each step.
    - Ensure that all derivations are presented in full detail:
    """
    
    prompts = create_multiple_prompts(base_prompt, response)
    results = await asyncio.gather(
        *[generate_and_return_ui(prompt,css_name_interst="derivation-section") for prompt in prompts]
    )
    html_results = [ui_to_html(result) for result in results]

    total_html = "".join(html_results)
    soup = BeautifulSoup(total_html, "html.parser")

    # Find the outermost div
    outer_div = soup.find("div")
    
    if outer_div:
        # Create a new div with the class "derivations-container"
        wrapper_div = soup.new_tag("div", **{"class": "derivations-container"})
        
        # Wrap the outer div with the new wrapper div
        outer_div.wrap(wrapper_div)
    
    return soup


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
        html = await generate_derivations_html(response = result)
        print(html)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

if __name__ == "__main__":
    asyncio.run(main())

