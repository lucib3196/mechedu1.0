from typing import Dict,Union
import asyncio

from numpy import mean
from . import metadata_chain
from  ..logging_config.logging_config import get_logger

# Set up the logger
logger = get_logger(__name__)

async def generate_module_metadata(question: str, user_data: Dict[str, str]) -> dict:
    logger.info("Generating initial metadata for the question.")
    
    # Generate the initial metadata
    initial_metadata = await metadata_chain.ainvoke({"question":question})
    logger.debug(f"Initial metadata: {initial_metadata}")
    initial_metadata = initial_metadata.dict()
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
    return metadata

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
