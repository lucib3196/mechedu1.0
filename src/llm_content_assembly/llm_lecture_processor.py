import asyncio
from typing import Dict, List, Tuple, Union
from ..llm_module_generator.agent.lecture_triaging_agent import lecture_triaging_agent
from . import extract_conceptual_questions, extract_computational_questions
from ..logging_config.logging_config import get_logger
from . import generate_conceputal_html_static,generate_derivation_html_static,generate_lecture_html_static
from .generate_module import generate_module_from_question
from . import conceptual_questions_parser, computational_question_parser

logger = get_logger(__name__)
user_data = {
    "created_by": "lberm007@ucr.edu",
    "code_language": "javascript"
}


async def extract_summary_and_key_concepts(image_paths: List[str]) -> Tuple:
    """
    Extracts summary and key concepts from lecture images and generates HTML.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        str: Generated HTML for the summary and key concepts section.
    """
    logger.info("Extracting summary and key concepts...\n")
    # Generate HTML for the summary section
    summary_html = await generate_lecture_html_static(image_paths)
    
    return summary_html[0] # type: ignore


async def extract_derivations(image_paths: List[str]) -> str:
    """
    Extracts derivations from lecture images and generates HTML.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        str: Generated HTML for the derivation section.
    """

    logger.info("Starting extraction of derivations...")

    # Generate HTML for the derivation section
    derivation_html = await generate_derivation_html_static(image_paths)
    return derivation_html


async def conceptual_question_extraction(image_paths: List[str]) -> Tuple[str, List[Tuple[str, str]]]:
    """
    Extracts conceptual questions from lecture images, generates modules, and HTML.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        Tuple[str, List[Tuple[str, str]]]: HTML for the conceptual questions section and a list of generated modules.
    """

    logger.info("Starting extraction of conceptual questions...")

    # Generate HTML for the conceptual question section
    conceptual_html = await generate_conceputal_html_static(image_paths)
    
    # Extract conceptual questions from the images
    conceptual_questions_images = await extract_conceptual_questions.send_request(image_paths)
    conceptual_question_list = conceptual_questions_parser(conceptual_questions_images)
    

    # Generate modules from extracted questions
    results: List[Dict[str, Union[str, int]]] = await asyncio.gather(
        *[generate_module_from_question(question, user_data) for question in conceptual_question_list]
    )
    
    modules = []
    for result in results:
        question_title = result.get("question_title", "")
        content = result.get("generated_content", "")
        modules.append((question_title, content))

    return conceptual_html, modules


async def computational_question_extraction(image_paths: List[str]) -> List[Tuple[str, str]]:
    """
    Extracts computational questions from lecture images and generates modules.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        List[Tuple[str, str]]: A list of generated modules.
    """
    global TOTAL_TOKENS
    
    logger.info("Extracting computational questions ...\n")
    
    # Extract computational questions from images
    computational_question_images = await extract_computational_questions.send_request(image_paths)
    computational_questions = computational_question_parser(response=computational_question_images)

    # Generate modules from extracted questions
    results = await asyncio.gather(
        *[generate_module_from_question(
            comp_question.get("question"), 
            user_data, 
            solution_guide=comp_question.get("solution")
        ) for comp_question in computational_questions]
    )
    
    modules = []
    for result in results:
        question_title = result.get("question_title", "")
        content = result.get("generated_content", "")
        modules.append((question_title, content))

    logger.info("Finished extracting computational questions")

    return modules


async def analyze_lecture(image_paths: List[str]) -> Tuple[str, List[Tuple[str, str]], int]:
    """
    Analyzes lecture images to extract and generate modules, summaries, and derivations.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        Tuple[str, List[Tuple[str, str]], int]: Combined HTML of all sections, all generated modules, and the total token count.
    """
    global TOTAL_TOKENS

    logger.info("Starting analysis of the lecture.")

    # Send request to the lecture triaging agent
    functions_to_execute = await lecture_triaging_agent.send_request(image_paths)

    logger.info(f"Agent determined functions to execute: {functions_to_execute}")

    # Prepare and run the tasks concurrently
    tasks = []
    async with asyncio.TaskGroup() as task_group:
        for function_name in functions_to_execute.get("functions_call", []):
            logger.info(f"Preparing to execute function: {function_name}")
            if function_name in globals():  # Check if the function is globally available
                function_to_call = globals()[function_name]
                task = task_group.create_task(function_to_call(image_paths), name=function_name)
                tasks.append(task)

    # Store the results in a dictionary, using function names as keys
    analysis_results = {}
    for task in tasks:
        task_name = task.get_name()
        analysis_results[task_name] = {"output": task.result()}
        logger.info(f"Task {task_name} completed.")

    htmls = []
    all_modules = []

    # Handle and store the output for each specific function, if executed
    if "extract_summary_and_key_concepts" in analysis_results:
        logger.info("Processing output from extract_summary_and_key_concepts.")
        htmls.append(analysis_results["extract_summary_and_key_concepts"]["output"])

    if "conceptual_question_extraction" in analysis_results:
        logger.info("Processing output from conceptual_question_extraction.")
        results = analysis_results["conceptual_question_extraction"]["output"]
        html, generated_modules = results
        htmls.append(html)
        all_modules.extend(generated_modules)

    if "extract_derivations" in analysis_results:
        logger.info("Processing output from extract_derivations.")
        htmls.append(analysis_results["extract_derivations"]["output"])

    if "computational_question_extraction" in analysis_results:
        logger.info("Processing output from computational_question_extraction.")
        generated_modules = analysis_results["computational_question_extraction"]["output"]
        all_modules.extend(generated_modules)

    # Combine the HTML results
    result_html = f"<body>{''.join(str(html) for html in htmls)}</body>"

    
    return result_html, all_modules


async def main():
    absolute_paths_input = input("Please enter the absolute paths of files or directory, separated by commas: ").strip()
    absolute_paths = [path.strip() for path in absolute_paths_input.split(',')]
    print(f"User provided paths: {absolute_paths}")
    await analyze_lecture(image_paths=absolute_paths)


if __name__ == "__main__":
    asyncio.run(main())