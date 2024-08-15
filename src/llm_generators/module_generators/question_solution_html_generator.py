import asyncio
from dataclasses import dataclass,field
import json

from ...semantic_search import ExampleBasedPromptDataFrame
from ...semantic_search.llm_config import LLMConfig
from .code_generator import ModuleCodeGenerator
from .module_generator_templates import solution_html_template
from ...credentials import api_key


llm_config = LLMConfig(api_key=api_key,model="gpt-4o-mini",temperature=0)

question_solution_generator = ModuleCodeGenerator(
    template=solution_html_template,
    example_input_column="question.html",
    example_output_column="solution.html",
    llm_config=llm_config
)

async def main():
    question = ["A car travels a long a straight road for a total time of 5 mphs for 30 minutes calculate the total distance"]
    generated = await question_solution_generator.arun(question)
    return generated

if __name__ == "__main__":
    asyncio.run(main())