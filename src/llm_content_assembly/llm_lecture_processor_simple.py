import asyncio
from typing import Dict, List, Tuple

from ..llm_module_generator.agent.lecture_triaging_agent import lecture_triaging_agent_simple
from ..llm_module_generator.ui_generator.ui_generators import (
    conceptual_ui_generator,
    derivation_ui_generator,
    summary_ui_generator
)
from ..llm_module_generator.image_extraction.image_llm_extraction import (
    extract_conceptual_questions
)
from ..llm_module_generator.parsers.parser import conceptual_questions_parser
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)

TOTAL_TOKENS = 0


async def extract_summary_and_key_concepts(image_paths: List[str]) -> str:
    """
    Extracts summary and key concepts from lecture images and generates HTML.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        str: Generated HTML for the summary and key concepts section.
    """
    global TOTAL_TOKENS

    logger.info("Extracting summary and key concepts...\n")

    # Generate HTML for the summary section
    summary_html = await summary_ui_generator.generate_multiple_ui(image_paths, "summary-section")

    # Update the total tokens used
    summary_tokens = summary_ui_generator.get_sum_tokens()
    TOTAL_TOKENS += summary_tokens

    logger.info(f"Tokens from summary extraction: {summary_tokens}, Total tokens: {TOTAL_TOKENS}")

    return summary_html


async def extract_derivations(image_paths: List[str]) -> str:
    """
    Extracts derivations from lecture images and generates HTML.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        str: Generated HTML for the derivation section.
    """
    global TOTAL_TOKENS

    logger.info("Starting extraction of derivations...")

    # Generate HTML for the derivation section
    derivation_html = await derivation_ui_generator.generate_multiple_ui(image_paths, "derivation-section")

    # Update the total tokens used after HTML generation
    derivation_tokens = derivation_ui_generator.get_sum_tokens()
    TOTAL_TOKENS += derivation_tokens

    logger.info(f"Tokens used for derivation extraction: {derivation_tokens}, Total tokens: {TOTAL_TOKENS}")

    return derivation_html


async def conceptual_question_extraction(image_paths: List[str]) -> str:
    """
    Extracts conceptual questions from lecture images and generates HTML.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        str: HTML for the conceptual questions section.
    """
    global TOTAL_TOKENS

    logger.info("Starting extraction of conceptual questions...")

    # Generate HTML for the conceptual question section
    conceptual_html = await conceptual_ui_generator.generate_multiple_ui(image_paths, "conceptual-question-section")

    # Update total tokens used after HTML generation
    conceptual_tokens_html = conceptual_ui_generator.get_sum_tokens()
    TOTAL_TOKENS += conceptual_tokens_html

    # Extract conceptual questions from the images
    conceptual_questions_images = await extract_conceptual_questions.send_request(image_paths)
    conceptual_question_list = conceptual_questions_parser(conceptual_questions_images)

    # Update total tokens used after question extraction
    conceptual_tokens_images = extract_conceptual_questions.get_total_tokens()
    TOTAL_TOKENS += conceptual_tokens_images

    logger.info(f"Tokens used for conceptual question extraction: {conceptual_tokens_images}, Total tokens: {TOTAL_TOKENS}")

    return conceptual_html


async def analyze_lecture_simple(image_paths: List[str]) -> Tuple[str, int]:
    """
    Analyzes lecture images to extract summaries, derivations, and conceptual questions, generating HTML content.

    Args:
        image_paths (List[str]): List of paths to the lecture images.

    Returns:
        Tuple[str, int]: Combined HTML of all sections and the total token count.
    """
    global TOTAL_TOKENS

    logger.info("Starting analysis of the lecture.")

    # Send request to the lecture triaging agent
    functions_to_execute = await lecture_triaging_agent_simple.send_request(image_paths)

    # Update total tokens used by the agent
    agent_tokens = lecture_triaging_agent_simple.get_total_tokens()
    TOTAL_TOKENS += agent_tokens

    logger.info(f"Agent determined functions to execute: {functions_to_execute}")
    logger.info(f"Tokens used by agent: {agent_tokens}, Total tokens: {TOTAL_TOKENS}")

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

    # Handle and store the output for each specific function, if executed
    if "extract_summary_and_key_concepts" in analysis_results:
        logger.info("Processing output from extract_summary_and_key_concepts.")
        htmls.append(analysis_results["extract_summary_and_key_concepts"]["output"])

    if "conceptual_question_extraction" in analysis_results:
        logger.info("Processing output from conceptual_question_extraction.")
        html = analysis_results["conceptual_question_extraction"]["output"]
        htmls.append(html)

    if "extract_derivations" in analysis_results:
        logger.info("Processing output from extract_derivations.")
        htmls.append(analysis_results["extract_derivations"]["output"])

    # Combine the HTML results
    result_html = f"<body>{''.join(str(html) for html in htmls)}</body>"

    logger.info(f"Total Tokens: {TOTAL_TOKENS}")

    return result_html, TOTAL_TOKENS


async def main():
    absolute_paths_input = input("Please enter the absolute paths of files or directory, separated by commas: ").strip()
    absolute_paths = [path.strip() for path in absolute_paths_input.split(',')]
    print(f"User provided paths: {absolute_paths}")
    result_html, total_tokens = await analyze_lecture_simple(image_paths=absolute_paths)
    print("Generated HTML Content:")
    print(result_html)
    print(f"Total tokens used: {total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())
