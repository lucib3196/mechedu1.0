# Standard library imports
import asyncio
import json
from dataclasses import dataclass, field
from venv import logger

from typing import Optional
# Third-party imports
import openai
from pydantic import BaseModel, Field
from openai import AsyncOpenAI


# Local application imports
from ..llm_base import LLM_Call, LLMConfig
from ...data_handler.example_based_prompt_formatter import ExampleBasedPromptDataFrame
from ...credentials import api_key
from ...logging_config.logging_config import get_logger
logger = get_logger(__name__)
from .module_generator_templates import question_html_gen_template,server_js_template_base,server_py_template_base,solution_html_template,question_html_gen_template_nonadaptive


@dataclass
class ModuleCodeGenerator(LLM_Call):
    llm_config: LLMConfig
    base_prompt: str
    example_input_column: str
    example_output_column: str
    threshold: float = 0.1
    num_examples: int = 2
    is_adaptive: bool = True
    def __post_init__(self):
        super().__post_init__()
        self.example_formatter = ExampleBasedPromptDataFrame(
            example_input_column=self.example_input_column,
            example_output_column=self.example_output_column,
            api_key=self.llm_config.api_key,
            is_adaptive=self.is_adaptive
        )

    def generate_prompt(self, question:str, additional_instructions=None)->str:
        prompt = self.example_formatter.format_examples_prompt(self.base_prompt,query=question,threshold=self.threshold,num_examples=self.num_examples)
        if additional_instructions:
            prompt += f"\n{additional_instructions}"
        prompt += f"\n\n BASED ON THIS KNOWLEDGE CONVERT THE FOLLOWING QUESTION INTO ITS RESPECTIVE HTML **new_question** {question} \n only generate the code"
        return prompt
    
    async def acall_generate_code(self, question:str, additional_instructions:str=None)->str:
        prompt = self.generate_prompt(question,additional_instructions)
        class Response(BaseModel):
            generated_code:str = Field(...,description="The generated code only return the generated code")
        response =await  self.acall(prompt, response_format=Response)
        try:
            if isinstance(response, str):
                extracted_response = json.loads(response)
            elif isinstance(response,dict):
                extracted_response = response
            return extracted_response.get('generated_code',0)
        except ValueError as e:
            logger.exception(f"Could not generate code and exeption {e} ")
            return None


# Define the LLM configuration with the specified model
llm_config = LLMConfig(api_key=api_key, model="gpt-4o-2024-08-06", temperature=0)

# Initialize all the generators
question_html_generator = ModuleCodeGenerator(
    base_prompt=question_html_gen_template,
    example_input_column="question",
    example_output_column="question.html",
    llm_config=llm_config
)
question_html_generator_nonadaptive = ModuleCodeGenerator(
    base_prompt=question_html_gen_template_nonadaptive,
    example_input_column="question",
    example_output_column="question.html",
    llm_config=llm_config,
    is_adaptive=False
)

question_solution_generator = ModuleCodeGenerator(
    base_prompt=solution_html_template,
    example_input_column="question.html",
    example_output_column="solution.html",
    llm_config=llm_config
)

server_js_generator = ModuleCodeGenerator(
    base_prompt=server_js_template_base,
    example_input_column="question.html",
    example_output_column="server.js",
    llm_config=llm_config
)

server_py_generator = ModuleCodeGenerator(
    base_prompt=server_py_template_base,
    example_input_column="question.html",
    example_output_column="server.py",
    llm_config=llm_config
)

async def main():
    # The question to be processed
    question = "A ball travels a distance of 5 meters during a period of 5 minutes determine its average speed"

    # Run all the generators concurrently using asyncio.gather
    results = await asyncio.gather(
        question_html_generator.acall_generate_code(question),
        question_html_generator_nonadaptive.acall_generate_code(question),
        question_solution_generator.acall_generate_code(question),
        server_js_generator.acall_generate_code(question),
        server_py_generator.acall_generate_code(question)
    )

    # Print the results
    for result in results:
        print(result)

    # Get and print the total tokens used by each generator
    question_html_tokens = question_html_generator.get_total_tokens()
    question_solution_tokens = question_solution_generator.get_total_tokens()
    server_js_tokens = server_js_generator.get_total_tokens()
    server_py_tokens = server_py_generator.get_total_tokens()

    # Print individual costs
    print(f"Tokens used by question_html_generator: {question_html_tokens}")
    print(f"Tokens used by question_solution_generator: {question_solution_tokens}")
    print(f"Tokens used by server_js_generator: {server_js_tokens}")
    print(f"Tokens used by server_py_generator: {server_py_tokens}")

    # Calculate and print the total cost
    total_tokens = (
        question_html_tokens +
        question_solution_tokens +
        server_js_tokens +
        server_py_tokens
    )
    print(f"Total tokens used: {total_tokens}")

if __name__ == "__main__":
    asyncio.run(main())