# Standard library imports
import asyncio
from dataclasses import dataclass, field
from typing import List

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from ..llm_base import LLM_Call, LLMConfig
from ...credentials import api_key
from .templates import generate_metadata_template

# LLM Configuration
llm_config = LLMConfig(api_key=api_key, model="gpt-4o-mini", temperature=0)

@dataclass
class GenerateMetadata(LLM_Call):
    llm_config: LLMConfig
    response_format: BaseModel
    base_prompt: str = generate_metadata_template

    def __post_init__(self):
        super().__post_init__()

    async def generate_metadata(self, question: str):
        prompt = self.base_prompt.format(question=question)
        return await self.acall(prompt, response_format=self.response_format)

class MetaData(BaseModel):
    uuid: str = Field(..., description="UUID: A universally unique identifier (UUID) for this item")
    title: str = Field(..., description="An appropriate title for the given question, returned using CamelCase format")
    stem: str = Field(..., description="Additional context or a subtopic related to the main topic")
    topic: str = Field(..., description="The main topic or subject of the educational content")
    tags: List[str] = Field(..., description="An array of keywords or tags associated with the content")
    prereqs: List[str] = Field(..., description="An array of prerequisites needed to access or understand the content")
    isAdaptive: bool = Field(..., description="Designates whether the content necessitates any form of numerical computation. 'true' if the question involves numerical computation, otherwise 'false'")

class Response(BaseModel):
    question: str = Field(..., description="The original question that was classified")
    metadata: MetaData
metadata_gen = GenerateMetadata(llm_config=llm_config, response_format=Response)
async def run_tests():
    
    test_questions = [
        "What is the capital of France?",
        "Explain the process of photosynthesis."
    ]
    
    for question in test_questions:
        result = await metadata_gen.generate_metadata(question)
        print(f"Question: {question}")
        print(f"Metadata: {result}")
        print(f"Tokens: {metadata_gen.get_total_tokens()}")

def main():
    asyncio.run(run_tests())

if __name__ == "__main__":
    main()

        