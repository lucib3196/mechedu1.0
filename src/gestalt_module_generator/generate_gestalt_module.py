from typing import Union, List,Dict,Any,Optional
from time import time
import asyncio
import json

from .utils import handle_image_inputs
from .generate_gestalt_metadata import generate_module_metadata
from ..llm_generators.module_generators.server_js_generator import server_js_generator
from ..llm_generators.module_generators.server_py_generator import server_py_generator
from ..llm_generators.module_generators.question_solution_html_generator import question_solution_generator
from ..llm_generators.module_generators.question_html_generator import question_html_generator

async def proccess_adaptive(question:str, metadata:dict, solution_guide:str=None,code_guide:str=None):
    question_html = await question_html_generator.arun(question)
    server_js, server_py,solution_html = await asyncio.gather(
        server_js_generator.arun(question),
        server_py_generator.arun(question),
        question_solution_generator.arun(question)
    )
    generated_content = {
        "question.html":question_html,
        "server.py": server_py,
        "server.js": server_js,
        "info.json": metadata,
        "solution.html": solution_html
    }
    return generated_content
async def proccess_nonadaptive(question:str, metadata:dict):
    question_html = await question_html_generator.arun(question)
    generated_content = {
        "question_html":question_html,
        "info.json": metadata,
    }
    return generated_content




async def generate_content(question:str,user_data:dict, solution_guide:str=None,code_guide:str=None):
    metadata = await generate_module_metadata(question,user_data)
    question_title = metadata.get("title","")
    print(f"Question Title: {question_title}")
    if metadata.get('isAdaptive', False) == True:
        generated_content = await proccess_adaptive(question,metadata)
        return generated_content
    else:
        generate_content = await proccess_nonadaptive(question,metadata)
        return json.dump(generate_content)
        

async def generate(user_input: Union[str, List[str]]):
    start_time = time()

    user_data = {
        "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
        "code_language": "javascript",
    }

    if isinstance(user_input, str):
        question = user_input
        results = await generate_content(question=question, user_data=user_data)
    
    elif isinstance(user_input, list):
        question_data = await handle_image_inputs(user_input)
        tasks = []

        for data in question_data:
            question = data.get("question", "")
            solution_guide = data.get("solution", "")
            tasks.append(asyncio.create_task(generate_content(question, user_data
            , solution_guide)))

        results = await asyncio.gather(*tasks)

        for result in results:
            print(f"Received Result: {result}")

    elapsed_time = time() - start_time
    print(f"Completed in {elapsed_time:.2f} seconds.")
    return results


if __name__ == "__main__" :
    image_path = [r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\test_images\textbook_ex1.png"]
    result = asyncio.run(generate(image_path))
    print(result)
    question = "A car travels a total distance of 5 miles in 10 minutes calculate its average speed"
    result = asyncio.run(generate(question))
    print(result)