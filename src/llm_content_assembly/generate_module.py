import asyncio
from typing import Tuple, Dict, Optional,Union
from .generate_adaptive_module import generate_adaptive_module
from .generate_nonadaptive_module import generate_nonadaptive
from .generate_module_metadata import generate_module_metadata
from .utils import extract_question_title, is_adaptive_question
from ..logging_config.logging_config import get_logger

# Initialize the logger
logger = get_logger(__name__)

TOKEN_COUNT = 0

from typing import Dict, Optional, Tuple

async def generate_module_from_question(
    question: str, 
    user_data: Dict[str, str], 
    solution_guide: Optional[str] = None
) -> Dict[str, Union[str, int]]:
    """
    Generates a module from a given question by first generating metadata,
    then determining if the question is adaptive or non-adaptive to generate
    the corresponding content.

    Args:
        question (str): The question for which the module is being generated.
        user_data (Dict[str, str]): A dictionary containing user-specific data 
            such as who created the module and the preferred code language.
        solution_guide (Optional[str]): An optional solution guide provided 
            for adaptive questions. Defaults to None.

    Returns:
        Dict[str, Union[str, int]]: A dictionary containing the question title, 
        the generated content, and the total token count used in generating the module.
    """
    global TOKEN_COUNT

    logger.info("Starting module generation from question.")
    
    # Generate metadata and count tokens
    metadata, metadata_tokens = await generate_module_metadata(question, user_data)
    question_title = extract_question_title(metadata)
    TOKEN_COUNT += metadata_tokens
    logger.debug(f"Metadata tokens: {metadata_tokens}, Total token count: {TOKEN_COUNT}")
    
    # Determine if the question is adaptive and generate content accordingly
    if is_adaptive_question(metadata):
        logger.info("Question identified as adaptive. Generating adaptive module.")
        generated_content, adaptive_tokens = await generate_adaptive_module(question, metadata, solution_guide)
    else:
        logger.info("Question identified as non-adaptive. Generating non-adaptive module.")
        generated_content, adaptive_tokens = await generate_nonadaptive(question, metadata)
    
    TOKEN_COUNT += adaptive_tokens
    logger.debug(f"Adaptive/Non-adaptive tokens: {adaptive_tokens}, Total token count: {TOKEN_COUNT}")

    logger.info("Module generation complete.")

    result = {
        "question_title": question_title,
        "generated_content": generated_content,
        "mod_tokens": TOKEN_COUNT
    }
    
    return result


async def main():
    logger.info("Running main function.")
    
    question = "A ball travels a total distance of 40 meters in 1 minute. Calculate its speed."
    user_data = {
        "created_by": "lberm007@ucr.edu",
        "code_language": "javascript"
    }
    
    result = await generate_module_from_question(question=question, user_data=user_data)
    
    logger.info("Main function execution complete.")
    logger.debug(f"Generated module result: {result}")
    
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
