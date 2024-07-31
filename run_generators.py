import os
from time import time
import asyncio
from typing import Union, List, Dict, Optional
from credentials import api_key
from src.llm_generators.metadata_generator import generate_metadata_and_update
from src.llm_generators.image_extraction import extract_question_image, extract_solution, code_guide_image
from src.llm_generators.CodeGenerators import question_html_generator,server_js_generator,server_py_generator,solution_html_generator

initial_data = {
    "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
    "code_language": "javascript",
    "generation_model":   "gpt-3.5-turbo-0125",
    "export_model": "gpt-3.5-turbo-0125",
    "solution_guide": None,  # Placeholder for solution guide path or content
    "export_path": "test_output"  # Replace with where you want questions to be exported
}

async def main(user_input: Union[str, List[str]]):
    start_time = time()
    try:
        if isinstance(user_input, str):
            question = user_input
            solution = None
            code_guide = None
        elif isinstance(user_input, list):
            question, solution, code_guide = await asyncio.gather(
                extract_question_image(user_input),
                extract_solution(user_input),
                code_guide_image(user_input)
            )
        else:
            raise ValueError("user_input must be either a string or a list of strings.")
        
        initial_metadata = await generate_metadata_and_update(question)
        print(f"Initial Metadata: {initial_metadata}")  # Debug print

        if "created_by" not in initial_data:
            raise KeyError("The key 'created_by' is missing from the initial metadata")

        metadata = {
            **initial_metadata,
            "createdBy": initial_data["created_by"],
            "qType": "num",
            "nSteps": 1,
            "updatedBy": "",
            "difficulty": 1,
            "codelang": initial_data["code_language"]
        }

        question_title = metadata.get("title")
        print(f"Question Title: {question_title}")

        if metadata.get('isAdaptive', "").lower() == "true":
            generated_content = await process_adaptive_async(question, metadata)
        else:
            generated_content = await process_nonadaptive_async(question, metadata)
        
        end_time = time()
        print(generated_content)
        print(f"Elapsed time: {end_time - start_time:.2f} seconds")
        return generated_content,question_title
    except Exception as e:
        print(f"An error occurred: {e}")


async def process_adaptive_async(question: str, metadata: Optional[str] = None,solution_guide:str=None, code_guide:str=None) -> Dict[str, str]:
    generated_question_html = await question_html_generator.arun(question)
    generated_py,generate_js, generated_solution = await asyncio.gather(
        server_py_generator.arun(generated_question_html,solution_guide),
        server_js_generator.arun(generated_question_html,solution_guide),
        solution_html_generator.arun(generated_question_html,solution_guide)
    )
    
    generated_content = {
        "question.html": generated_question_html,
        "server.py": generated_py,
        "server.js": generate_js,
        "info.json": str(metadata),
        "solution.html": generated_solution
    }
    return generated_content

async def process_nonadaptive_async(question: str, metadata: Optional[str] = None) -> Dict[str, str]:
    generated_question_html = await question_html_generator.arun(question)
    generated_solution = await question_html_generator.arun(generated_question_html)
    
    generated_content = {
        "question.html": generated_question_html,
        "info.json": str(metadata) if metadata is not None else '',
        "solution.html": generated_solution
    }
    return generated_content


## Test
question = """Classify each number as being a natural number (N), whole number (W), integer (I), rational number (Q), and/or irrational number (Q′).

- \(\sqrt{36}\)
- \(\frac{8}{3}\)
- \(\sqrt{73}\)
- \(-6\)
- \(3.2121121112\ldots\)
"""

asyncio.run(main(question))