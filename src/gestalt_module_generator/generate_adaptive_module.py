import asyncio

from typing import Dict


from ..llm_generators.module_generators.server_js_generator import server_js_generator
from ..llm_generators.module_generators.server_py_generator import server_py_generator
from ..llm_generators.module_generators.question_solution_html_generator import question_solution_generator
from ..llm_generators.module_generators.question_html_generator import question_html_generator
from ..llm_generators.llm_templates import server_template_code_guide, solution_improvement_prompt



async def process_adaptive_question(question: str, metadata_dict: dict, solution_guide: str = None)->Dict:
    """_summary_

    Args:
        question (str): Question to be generated
        metadata_dict (dict): metadata of the question will be saved with contnet
        solution_guide (str, optional): A solution guide to the question, this helps out when generating the code. Defaults to None.

    Returns:
        Dict: _description_
    """
    question_html = await question_html_generator.arun(question)

    additional_instructions = f"{server_template_code_guide} \n {solution_guide}" if solution_guide else None
    print(f"\n This is the solution guide: {solution_guide if solution_guide else 'No solution guide provided'} \n")

    try:
        server_js, server_py, solution_html = await asyncio.gather(
            server_js_generator.arun(question_html, additional_instruction=additional_instructions),
            server_py_generator.arun(question_html, additional_instruction=additional_instructions),
            question_solution_generator.arun(question_html, additional_instruction=additional_instructions)
        )
    except Exception as e:
        print(f"Error during processing: {e}")
        raise

    generated_content = {
        "question.html": question_html,
        "server.py": server_py,
        "server.js": server_js,
        "info.json": metadata_dict,
        "solution.html": solution_html
    }
    return generated_content
