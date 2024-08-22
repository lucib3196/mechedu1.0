from openai import AsyncOpenAI

import asyncio
from pydantic import BaseModel, Field
from dataclasses import dataclass,field
import json

from ...semantic_search import ExampleBasedPromptDataFrame
from ...semantic_search.llm_config import LLMConfig


@dataclass
class ModuleCodeGenerator:
    template: str
    example_input_column: str
    example_output_column: str
    llm_config: LLMConfig
    threshold: float = 0.3
    num_examples: int = 2
    
    def __post_init__(self):
        self.example_formatter = ExampleBasedPromptDataFrame(
            example_input_column=self.example_input_column,
            example_output_column=self.example_output_column,
            api_key=self.llm_config.api_key,
        )
        self.client_async = AsyncOpenAI(api_key=self.llm_config.api_key)
        self.model = self.llm_config.model
    
    def generate_prompt(self,question:str, additional_instruction:str=None)->None:
        prompt = self.example_formatter.format_examples_prompt(self.template, query=question,threshold=self.threshold,num_examples=self.num_examples)
        if additional_instruction:
            prompt += f"\n{additional_instruction}"
        prompt += f"\n new_question {question} \n Only return the generated code"
        return prompt
    
    async def arun(self,question:str, additional_instruction:str=None):
        prompt = self.generate_prompt(question,additional_instruction)
        print(f"This is the prompt {prompt}\n")
        class Response(BaseModel):
            generated_code:str = Field(...,description="The generated code only return the generated code")

        print(f"This is the model{self.model}")
        response = await self.client_async.beta.chat.completions.parse(
        model=self.llm_config.model,
        messages=[
            {"role": "system", "content": "You are a professor at a University focused on mechanical engineering education."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format=Response
        )
        generated_code = json.loads(response.choices[0].message.content)
        # print(f"Generated code  {generated_code.get('generated_code',0)}\n")
        return generated_code.get('generated_code',0)

    


async def main():
    input_columns ="question"
    output = "question.html"
    from ...credentials import api_key
    exampe_based_formatter = ExampleBasedPromptDataFrame(example_input_column=input_columns,example_output_column=output,api_key=api_key)


    prompt = "Hello"
    question = "A ball travels a distance of 5 meters"
    print(exampe_based_formatter.format_examples_prompt(template_text=prompt,query=question,threshold=0.2,num_examples=3))

    llm_config = LLMConfig(api_key=api_key, model="gpt-4o-mini",temperature=0)
    code_gen = ModuleCodeGenerator(template=prompt,example_input_column=input_columns,example_output_column=output,llm_config=llm_config)
    await code_gen.arun(question)

    
if __name__ == "__main__":
    asyncio.run(main())