# Standard library imports
import asyncio
import langchain_core.messages
import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
# Third-party imports
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain import hub

# Local application imports
from ...data_handler.example_based_prompt_formatter import ExampleBasedPromptDataFrame
from ...logging_config.logging_config import get_logger
from langchain.prompts import HumanMessagePromptTemplate
# Load .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize logger
logger = get_logger(__name__)


@dataclass
class ModuleCodeGenerator:
    model: str
    base_prompt: str
    example_input_column: str
    example_output_column: str
    response: BaseModel
    threshold: float = 0.0
    num_examples: int = field(default=1)
    is_adaptive: bool = True

    def __post_init__(self):
        self.example_formatter = ExampleBasedPromptDataFrame(
            example_input_column=self.example_input_column,
            example_output_column=self.example_output_column,
            is_adaptive=self.is_adaptive
        )
        self.llm = ChatOpenAI(model=self.model)
        try:
            self.base = self.base_prompt.messages[0].prompt.template
        except:
             self.base = self.base_prompt.messages[0]



    def generate_prompt(self, query: str, additional_instructions: Optional[str] = None,solution_guide:Optional[str]=None) -> str:
        prompt = self.example_formatter.format_examples_prompt(
            self.base,
            query=query,
            threshold=self.threshold,
            num_examples=self.num_examples
        )
        prompt += (
            f"\n\n BASED ON THIS KNOWLEDGE CONVERT THE FOLLOWING QUESTION INTO ITS RESPECTIVE "
            f"CODE **new_question** {query} \nOnly return the generated code"
        )
        if solution_guide:
            prompt += f"""SOLUTION GUIDE: The user provided a solution guide Analyze 
            the following solution guide and ensure that all logic provided is correctly 
            implemented in any generated code. When generating code, use the solution steps and 
            calculations as the foundation for the computation, adhering strictly to the logic provided in the guide.
            {solution_guide} """
        if additional_instructions:
            prompt += f"\nADDITIONAL INSTRUCTIONS: {additional_instructions}\n"
        return prompt

    async def acall_generate_code(self, query: str, additional_instructions: Optional[str] = None,solution_guide:Optional[str]=None):
        prompt = self.generate_prompt(query, additional_instructions,solution_guide=solution_guide)
        response = await self.llm.with_structured_output(self.response).ainvoke([prompt])
        response = response.dict()
        return response.get("generated_code","")

    
class Response(BaseModel):
    generated_code:str = Field(...,description="The generated code only return the generated code")

question_html_generator = ModuleCodeGenerator(
    base_prompt=hub.pull("question_html_template"),
    model="gpt-4o-mini",
    response=Response,
    example_input_column="question",
    example_output_column="question.html",
    num_examples = 2
)
question_html_generator_nonadaptive = ModuleCodeGenerator(
    base_prompt=hub.pull("question_html_template"),
    model="gpt-4o-mini",
    response=Response,
    example_input_column="question",
    example_output_column="question.html",
    num_examples = 3,
    is_adaptive=False
)
question_solution_generator = ModuleCodeGenerator(
    base_prompt=hub.pull("solution_html_template"),
    example_input_column="question.html",
    example_output_column="solution.html",
    model="gpt-4o-mini",
    response=Response,
    num_examples = 1
)
question_solution_generator_flask = ModuleCodeGenerator(
    base_prompt=hub.pull("solution_html_flask"),
    example_input_column="question.html",
    example_output_column="solution.html",
    model="gpt-4o-mini",
    response=Response,
    num_examples = 0
)
server_js_generator = ModuleCodeGenerator(
    base_prompt=hub.pull("server_js_template_base"),
    example_input_column="question.html",
    example_output_column="server.js",
    model="gpt-4o-mini",
    response=Response,
    num_examples = 1
)
server_py_generator = ModuleCodeGenerator(
    base_prompt=hub.pull("server_py_template_base1"),
    example_input_column="question.html",
    example_output_column="server.py",
    model="gpt-4o-mini",
    response=Response,
    num_examples = 1
)

async def main():
    # The question to be processed
    question = ("How much should be deposited at t = 0 into a fund paying 3% compounded per period in order to withdraw "
                "$2000 at t = 1, $1500 at t = 3, and $750 at t = 7 such that the fund is depleted at the last withdrawal?")

    # Run all the generators concurrently using asyncio.gather
    results = await asyncio.gather(
        question_html_generator.acall_generate_code(question),
        question_solution_generator.acall_generate_code(question),
        server_js_generator.acall_generate_code(
            question,
            additional_instructions=("I want to generate different possible periods ranging from 1-10 and have interest values "
                                     "between 1-5%, then I want the withdrawals to be between 1000-5000 chosen randomly, "
                                     "and then I want the amounts of withdrawals to be random.")
        ),
        server_py_generator.acall_generate_code(question)
    )

    # Print the results
    for idx, result in enumerate(results, 1):
        print(f"RESULT {idx}:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())