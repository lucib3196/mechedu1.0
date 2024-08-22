from ..llm_generators.module_generators.server_js_generator import server_js_generator
from ..llm_generators.module_generators.server_py_generator import server_py_generator
from ..llm_generators.module_generators.question_solution_html_generator import question_solution_generator
from ..llm_generators.module_generators.question_html_generator import question_html_generator
from ..llm_generators.llm_templates import server_template_code_guide, solution_improvement_prompt



async def process_nonadaptive_question(question:str, metadata_dict:dict)->dict:
    """Generates a module for questions that do not require 
    code files ie basically multiple choice questions

    Args:
        question (str): Question to be used for module creation
        metadata_dict (dict): metadata to be saved for question

    Returns:
        dict: A collection of generated content with file names and content
    """
    try:
        question_html = await question_html_generator.arun(question)
    except Exception as e:
        print(f"Error during processing: {e}")
        raise
    generated_content = {
            "question.html":question_html,
            "info.json": metadata_dict,

        }
    return generated_content
