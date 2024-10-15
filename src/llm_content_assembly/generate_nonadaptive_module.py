import asyncio
from . import question_html_generator_nonadaptive
import asyncio
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)



async def generate_nonadaptive(question: str, metadata_dict: dict=None,instructions:dict = {}) -> dict:
    """Generates a module for questions that do not require code files, 
    such as multiple-choice questions.

    Args:
        question (str): Question to be used for module creation.
        metadata_dict (dict): Metadata to be saved for the question.

    Returns:
        dict: A collection of generated content with file names and content.
    """
    try:
        question_instructions = instructions.get("question_html_instructiosn","")
        # Generate the HTML for the question
        question_html = await question_html_generator_nonadaptive.acall_generate_code(question,additional_instructions=question_instructions)
        
        # Prepare the generated content
        generated_content = {
            "question.html": question_html,
            "info.json": metadata_dict
        }
        
    except Exception as e:
        logger.error(f"Error during processing of non-adaptive question '{question}': {e}")
        raise

    return generated_content


async def main():
    questions = [
        "What is the capital of France?",
        "What is the boiling point of water at sea level?",
        "Which planet is closest to the sun?",
    ]
    metadata_dict = {"source": "Generated via process_nonadaptive_question"}

    # Run the module generation concurrently for all questions
    results = await asyncio.gather(*(generate_nonadaptive(question, metadata_dict) for question in questions))

    # Process the results and sum the total tokens
    for result in results:
        logger.info(f"Generated content:\n{result}\n")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())
