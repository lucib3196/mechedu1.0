from typing import Dict,Union
import asyncio

from numpy import mean
from ..llm_module_generator.physics_module_generator.generate_metadata import metadata_gen
from  ..logging_config.logging_config import get_logger

# Set up the logger
logger = get_logger(__name__)

async def generate_module_metadata(question: str, user_data: Dict[str, str]) -> tuple[Dict[str, Union[str, bool, int]], int]:
    logger.info("Generating initial metadata for the question.")
    
    # Generate the initial metadata
    initial_metadata = await metadata_gen.generate_metadata(question)
    logger.debug(f"Initial metadata: {initial_metadata}")

    # Create the final metadata dictionary by adding additional fields
    metadata = {
        **initial_metadata.get("metadata", {}),
        "createdBy": user_data.get("created_by", ""),
        "qType": "num",
        "nSteps": 1,
        "updatedBy": "",
        "difficulty": 1,
        "codelang": user_data.get("code_language", ""),
        "reviewed": False
    }
    
    logger.info("Final metadata generated.")
    logger.debug(f"Final metadata: {metadata}")

    logger.info(f"Token Count {metadata_gen.get_total_tokens()}")
    
    return metadata,metadata_gen.get_total_tokens()

async def main():
    logger.info("Starting main function.")
    
    question = "A car travels a total distance of 50 miles in 2 hours, what was its average speed?"
    user_data = {
        "created_by": "lberm007@ucr.edu",
        "code_language": "javascript"
    }
    
    result = await generate_module_metadata(question, user_data=user_data)
    
    logger.info("Metadata generation complete.")
    logger.debug(f"Generated metadata: {result}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)
