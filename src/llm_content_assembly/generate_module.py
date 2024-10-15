import asyncio
from typing import Tuple, Dict, Optional,Union
from .generate_module_metadata import generate_module_metadata
from .utils import extract_question_title, is_adaptive_question
from ..logging_config.logging_config import get_logger
from . import chain
from .generate_adaptive_module import generate_adaptive_module
from .generate_nonadaptive_module import generate_nonadaptive

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

    logger.info("Starting module generation from question.")
    
    # Initial analysis of the question to determine any specific instructions
    analysis = await chain.ainvoke({"query": question})
    analysis = analysis.dict()
    question = analysis.get("question")
    question_html_instructions = analysis.get("question_html_instructions")
    server_instructions = analysis.get("server_instructions")
    instructions ={
        "question_html_instructiosn": analysis.get("question_html_instructions"),
        "server_instructions": analysis.get("server_instructions"),
        "solution_guide": solution_guide if not None else None
    }

    # Generate metadata and get title
    metadata = await generate_module_metadata(question, user_data)
    question_title = extract_question_title(metadata)
    

    # Determine if the question is adaptive and generate content accordingly
    if is_adaptive_question(metadata):
        logger.info("Question identified as adaptive. Generating adaptive module.")
        generated_content = await generate_adaptive_module(question, metadata, instructions=instructions)
    else:
        logger.info("Question identified as non-adaptive. Generating non-adaptive module.")
        generated_content = await generate_nonadaptive(question, metadata,instructions=instructions)
    

    logger.info("Module generation complete.")

    result = {
        "question_title": question_title,
        "generated_content": generated_content
    }
    
    return result


async def main():
    logger.info("Running main function.")
    
    question = "A ball travels a total distance of 40 meters in 1 minute. Calculate its speed. I want this question to contain different unit systems specifically for SI I want to have m, km and m/s and km/s while for USCS i want to have ft, ft/s, mph and miles. I want proper conversion for everything"
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
