from typing import Union, List, Dict, Optional
import asyncio
from ..llm_generators.module_generators.metadata_generator import classify_question


user_data = {
    "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
    "code_language": "javascript",
}
async def  generate_module_metadata(question: str, user_data: dict) -> dict:
    initial_metadata = await classify_question(question)
    metadata = {
        **initial_metadata.get("metadata"),  # Unpack initial metadata into the new dictionary
        "createdBy": user_data.get("created_by"),  # Add additional metadata fields
        "qType": "num",
        "nSteps": 1,
        "updatedBy": "",
        "difficulty": 1,
        "codelang": user_data.get("code_language"),
        "reviewed": False
    }
    return metadata


async def main():
    question= "A car travels a total distance of 50 miles in 2 hours, what was its average speed"
    return await generate_module_metadata(question, user_data= user_data)

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)