from .generate_ui import generate_and_return_ui
from .generate_html_from_ui import ui_to_html
from ..image_extraction.extract_summary_images import extract_summary_and_key_concepts_image
import asyncio
import os
import json
from typing import List
from bs4 import BeautifulSoup
import os
import asyncio

def generate_lecture_summary_prompt(response: dict) -> str:
    analysis = response.get("analysis", {})
    
    summary = analysis.get("summary", "No summary provided.")
    key_concepts = analysis.get("key_concepts", "No key concepts provided.")
    foundational_concepts = analysis.get("foundational_concepts", "No foundational concepts provided.")
    
    prompt = f"""
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate.
    You are only focused on working on the following sections. When you need to format any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters to ensure proper rendering.

    **Instructions:**

    1. **Summary of Lecture**: Create a section that provides a concise overview of the lecture's main points. Use appropriate headings and bullet points to make the content easily digestible.
       - Ensure every detail provided is included: Summary:  {summary}

    2. **Key Concepts**: Highlight the essential concepts covered in the lecture. Clearly define each concept, and where applicable, accompany them with relevant examples or illustrations. Organize the content effectively using HTML elements like lists or tables.
       - Include every piece of information provided: Key Concept:  {key_concepts}

    3. **Foundational Concepts**: Detail the foundational concepts that underlie the lecture material. This section should thoroughly explain each concept and its relevance to the lecture's topic.
       - Include every piece of information provided: Foundational Concepts: {foundational_concepts}

    Ensure proper formatting of the content and include all content present.
    """
    
    return prompt

async def generate_lecture_summary_html(response:dict)->str:
    prompt = generate_lecture_summary_prompt(response)
    result_ui = await generate_and_return_ui(prompt,"summary_and_key_concepts")
    html = ui_to_html(result_ui)
    return html 


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
        result = await extract_summary_and_key_concepts_image(image_paths=image_paths)
        html = await generate_lecture_summary_html(response = result)
        print(html)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

if __name__ == "__main__":
    asyncio.run(main())