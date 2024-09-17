import asyncio
from ..llm_module_generator.physics_module_generator.module_generator import question_html_generator, question_solution_generator, server_js_generator, server_py_generator,question_html_generator_nonadaptive
import asyncio
from ..llm_module_generator.physics_module_generator.llm_templates import server_template_code_guide, solution_improvement_prompt
from ..llm_module_generator.question_html_ui.question_html_builder import question_html_builder_advance
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)



async def generate_nonadaptive(question: str, metadata_dict: dict=None) -> dict:
    """Generates a module for questions that do not require code files, 
    such as multiple-choice questions.

    Args:
        question (str): Question to be used for module creation.
        metadata_dict (dict): Metadata to be saved for the question.

    Returns:
        dict: A collection of generated content with file names and content.
    """
    try:
        # Generate the HTML for the question
        question_html = await question_html_builder_advance.generate_html_ui(question)
        
        # Get and log total tokens used
        question_html_tokens = question_html_generator_nonadaptive.get_total_tokens()
        logger.info(f"Tokens used for non-adaptive question '{question}': {question_html_tokens}")
        
        # Prepare the generated content
        generated_content = {
            "question.html": question_html,
            "info.json": metadata_dict
        }
        
    except Exception as e:
        logger.error(f"Error during processing of non-adaptive question '{question}': {e}")
        raise

    return generated_content, question_html_tokens


async def main():
    questions = [
        "What is the capital of France?",
        "What is the boiling point of water at sea level?",
        "Which planet is closest to the sun?",
    ]

    total_tokens_used = 0
    metadata_dict = {"source": "Generated via process_nonadaptive_question"}

    # Run the module generation concurrently for all questions
    results = await asyncio.gather(*(generate_nonadaptive(question, metadata_dict) for question in questions))

    # Process the results and sum the total tokens
    for result in results:
        total_tokens_used += result["total_tokens"]
        logger.info(f"Generated content:\n{result}\n")

    logger.info(f"Total tokens used across all non-adaptive questions: {total_tokens_used}")
    return total_tokens_used

if __name__ == "__main__":
    asyncio.run(main())
