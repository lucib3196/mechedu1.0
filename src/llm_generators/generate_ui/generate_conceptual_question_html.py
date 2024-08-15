import asyncio
import os
import json
from typing import List
from bs4 import BeautifulSoup
import os
import asyncio


from .generate_html_from_ui import ui_to_html
from .generate_ui import generate_and_return_ui
from ..image_extraction.conceputual_question_extraction_images import conceptual_question_extraction_images

def extract_conceptual_questions(response: dict) -> List[str]:
    conceptual_questions = response.get("questions", [])
    
    all_questions = []
    
    for conceptual_question in conceptual_questions:
        question_text = f"Question: {conceptual_question.get('question', 'Unknown')}"
        
        # Handle multiple choice options
        multiple_choice_options = conceptual_question.get('multiple_choice_options', [])
        options_text = "\n".join(f" - Option: {option}" for option in multiple_choice_options)
        
        # Add correct answer
        correct_answer = f"Correct Answer: {conceptual_question.get('correct_answer', 'No answer provided')}"
        
        # Combine the question, options, and correct answer into a single string
        combined_text = f"{question_text}\n{options_text}\n{correct_answer}"
        
        all_questions.append(combined_text)
    
    return all_questions

def create_multiple_prompts(base_prompt: str, response: dict) -> List[str]:
    derivations = extract_conceptual_questions(response)
    return [base_prompt + derivation for derivation in derivations]

async def generate_conceptual_questions_html(response: dict) -> BeautifulSoup:
    base_prompt = """
    You are a web developer tasked with creating an engaging and informative HTML webpage based on the following extracted lecture notes. The webpage should be well-structured, visually appealing, and easy to navigate.
    You are only focused on working on the following sections. When you need to format any mathematical symbols or equations, use LaTeX enclosed within appropriate delimiters to ensure proper rendering.

    **Instructions:**

    1. **Conceptual Questions**: Create a section dedicated to multiple-choice conceptual questions based on the lecture material. Each question should be clearly presented, with four possible answer choices labeled (A), (B), (C), and (D). Indicate the correct answer for each question.
    - Ensure that all questions and answer choices are formatted using appropriate HTML tags to enhance readability.
    - If any mathematical notation is required within the questions or answer choices, use LaTeX to format it properly.
    """

    
    prompts = create_multiple_prompts(base_prompt, response)
    results = await asyncio.gather(
        *[generate_and_return_ui(prompt,"conceptual-question-section") for prompt in prompts]
    )
    html_results = [ui_to_html(result) for result in results]

    total_html = "".join(html_results)
    soup = BeautifulSoup(total_html, "html.parser")

    # Find the outermost div
    outer_div = soup.find("div")
    
    if outer_div:
        # Create a new div with the class "derivations-container"
        wrapper_div = soup.new_tag("div", **{"class": "conceptual_question_container"})
        
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
        result = await conceptual_question_extraction_images(image_paths=image_paths)
        html = await generate_conceptual_questions_html(response = result)
        print(html)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    

if __name__ == "__main__":
    asyncio.run(main())