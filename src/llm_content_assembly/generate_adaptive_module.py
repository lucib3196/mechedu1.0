# Standard library imports
import asyncio
from typing import Optional, Tuple, Dict, Any

# Local imports
from src.logging_config import get_logger
from ..llm_module_generator.physics_module_generator import (
    math_js_retriever,
    module_generator,
    pl_retriever,
    templates,
)
from ..llm_module_generator import analyze_input_query

# Initialize logger
logger = get_logger(__name__)


async def generate_question_html(question_instructions: str) -> str:
    """
    Generates HTML content for the given question instructions.

    Args:
        question_instructions (str): Instructions for generating question HTML.

    Returns:
        str: Generated question HTML.
    """
    logger.info("Generating question HTML...")
    try:
        question_html = await module_generator.question_html_generator.acall_generate_code(
            question_instructions
        )
        logger.info("Finished generating question HTML.")
        return question_html
    except Exception as e:
        logger.error(f"Failed to generate question HTML: {e}", exc_info=True)
        raise


def prepare_additional_instructions(solution_guide: Optional[str] = None) -> Optional[str]:
    """
    Prepares additional instructions based on the solution guide.

    Args:
        solution_guide (Optional[str], optional): Instructions for solution improvement. Defaults to None.

    Returns:
        Optional[str]: Formatted additional instructions or None.
    """
    if solution_guide:
        instructions = f"{templates.server_template_code_guide}\n{solution_guide}"
        logger.info("Solution guide provided. Preparing additional instructions.")
        return instructions
    logger.info("No solution guide provided.")
    return None


async def generate_server_and_solution(
    question_html: str,
    additional_instructions: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Generates server JS, server PY, and solution HTML concurrently.

    Args:
        question_html (str): The HTML content of the question.
        additional_instructions (Optional[str], optional): Instructions for server JS generation. Defaults to None.

    Returns:
        Tuple[str, str, str]: Server JS, Server PY, and Solution HTML content.
    """
    try:
        logger.info("Generating server JS, server PY, and solution HTML concurrently.")
        server_js_task = module_generator.server_js_generator.acall_generate_code(
            question_html, additional_instructions=additional_instructions[0]
        )
        server_py_task = module_generator.server_py_generator.acall_generate_code(
            question_html ,additional_instructions=additional_instructions[1] # No additional instructions for server PY
        )
        solution_html_task = module_generator.question_solution_generator.acall_generate_code(
            question_html,additional_instructions=additional_instructions[2]  # No additional instructions for solution HTML
        )

        server_js, server_py, solution_html = await asyncio.gather(
            server_js_task,
            server_py_task,
            solution_html_task,
        )
        logger.info("Successfully generated server JS, server PY, and solution HTML.")
        return server_js, server_py, solution_html
    except Exception as e:
        logger.error(f"Error during server and solution generation: {e}", exc_info=True)
        raise


def calculate_total_tokens() -> int:
    """
    Calculates the total number of tokens used across all generators.

    Returns:
        int: The total number of tokens used.
    """
    try:
        logger.info("Calculating total tokens used across all generators.")
        question_html_tokens = module_generator.question_html_generator.get_total_tokens()
        server_js_tokens = module_generator.server_js_generator.get_total_tokens()
        server_py_tokens = module_generator.server_py_generator.get_total_tokens()
        solution_html_tokens = module_generator.question_solution_generator.get_total_tokens()

        total_tokens = (
            question_html_tokens +
            server_js_tokens +
            server_py_tokens +
            solution_html_tokens
        )
        logger.info(f"Total tokens used: {total_tokens}")
        return total_tokens
    except Exception as e:
        logger.error(f"Failed to calculate total tokens: {e}", exc_info=True)
        raise


async def generate_adaptive_module(
    question: str,
    metadata_dict: Optional[Dict[str, Any]] = None,
    solution_guide: Optional[str] = None
) -> Tuple[Dict[str, Any], int]:
    """
    Generates adaptive module content based on the provided question.

    This function performs the following steps:
    1. Analyzes the input question.
    2. Retrieves MathJS and PL code snippets concurrently.
    3. Generates HTML content for the question.
    4. Prepares additional instructions for server JS generation.
    5. Generates server-side JavaScript, Python code, and solution HTML concurrently.
    6. Calculates the total number of tokens used.
    7. Compiles all generated content into a dictionary.

    Args:
        question (str): The question to generate content for.
        metadata_dict (Optional[Dict[str, Any]], optional): Additional metadata. Defaults to None.
        solution_guide (Optional[str], optional): Instructions for solution improvement. Defaults to None.

    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the generated content dictionary and total tokens used.
    """
    try:
        # Step 1: Analyze the input question
        logger.info("Analyzing input question.")
        analyzed_question = await analyze_input_query(question)
        logger.debug(f"Analyzed Question: {analyzed_question}")

        # Step 2: Retrieve MathJS and PL code snippets concurrently
        logger.info("Retrieving MathJS and PL code snippets.")
        math_js_snippets, pl_snippets = await asyncio.gather(
            math_js_retriever.mathjs_code_snippet_chain(analyzed_question),
            pl_retriever.pl_code_snippet_chain(analyzed_question)
        )
        logger.debug(f"MathJS Snippets: {math_js_snippets}")
        logger.debug(f"PL Snippets: {pl_snippets}")

        # Step 3: Generate HTML instructions for the question
        question_html_instructions = f"{analyzed_question}\n{pl_snippets}"
        logger.debug(f"Question HTML Instructions: {question_html_instructions}")

        # Step 4: Generate question HTML
        question_html = await generate_question_html(question_html_instructions)

        # Step 5: Prepare additional instructions (only for server JS generation)
        solution_instructions = prepare_additional_instructions(solution_guide)

        # Combine MathJS snippets with solution instructions for server JS generator
        if solution_instructions:
            server_js_additional_instructions = f"{math_js_snippets}\n{solution_instructions}"
            additional_instructions = [server_js_additional_instructions,solution_instructions,solution_instructions]
        else:
            server_js_additional_instructions = math_js_snippets
            additional_instructions = [math_js_snippets,None,None]

        # Step 6: Generate server JS, server PY, and solution HTML concurrently
        server_js, server_py, solution_html = await generate_server_and_solution(
            question_html, additional_instructions=additional_instructions
        )

        # Step 7: Calculate total tokens used
        total_tokens = calculate_total_tokens()

        # Step 8: Compile generated content into a dictionary
        generated_content = {
            "question.html": question_html,
            "server.py": server_py,
            "server.js": server_js,
            "info.json": metadata_dict if metadata_dict else {},
            "solution.html": solution_html,
        }
        logger.debug(f"Generated Content: {generated_content}")

        return generated_content, total_tokens

    except Exception as e:
        logger.error(f"An error occurred in generate_adaptive_module: {e}", exc_info=True)
        raise




async def main():
    questions = [
        # "Calculate the thermal efficiency of a heat engine with an input heat of 500 kJ and work output of 200 kJ."
        # "Determine the lift force on an aircraft wing if the lift coefficient is 0.4, the air density is 1.225 kg/m^3, the wing area is 25 m^2, and the velocity of the aircraft is 50 m/s.",
        # "Calculate the output voltage of a resistor-capacitor (RC) circuit with an input voltage of 10V, resistance of 1 kΩ, and capacitance of 100 µF after 5 seconds.",
        # "Determine the maximum tensile stress a steel rod can withstand if it has a diameter of 10 mm and a tensile force of 20 kN is applied.",
        # "Calculate the volume of material needed to 3D print a solid cylindrical part with a diameter of 50 mm and a height of 100 mm."
        "I want to generate a question that will ask students to calculate the derivative of a function at most degree 4 but can have as low as 2 using the power rule and have random coefficients"
    ]

    total_tokens_used = 0

    # Run the module generation concurrently for all questions
    results= await asyncio.gather(*(generate_adaptive_module(question) for question in questions))

    # Process the results and sum the total tokens
    for result in results:
        total_tokens_used += int(result[1])
        logger.info(f"Generated content:\n{result[0]}\n")

    logger.info(f"Total tokens used across all questions: {total_tokens_used}")
    return total_tokens_used

if __name__ == "__main__":
    asyncio.run(main())
