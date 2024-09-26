# Standard library imports
import asyncio
from dataclasses import dataclass, field
import token

# Third-party imports
from bs4 import BeautifulSoup
import json
# Local imports
from .ui_builder import LLMUIBuilder, LLMConfig, UI
from ..image_extraction import (
    extract_summary,
    extract_computational_questions,
    extract_derivations,
    extract_conceptual_questions,
    ImageToLLMProcessor
)
from .ui_prompts import conceptual_question_ui_prompt, derivation_ui_prompt, summary_ui_prompt
from ...credentials import api_key
from ...logging_config.logging_config import get_logger
from ..parsers.parser import conceptual_questions_parser, derivations_parser, lecture_summary_parser


logger = get_logger(__name__)

@dataclass
class MultiUIContentGenerator(LLMUIBuilder):
    base_prompt: str
    extractor: ImageToLLMProcessor    # You can pass your own extractor object
    parser: callable  # You can pass your own parser function
    total_tokens: int = field(default=0, init=False)

    def __post_init__(self):
        super().__post_init__()
        if not hasattr(self.extractor, 'send_request') or not callable(self.extractor.send_request):
            raise ValueError("Extractor must have a 'send_request' method")
        if not hasattr(self.extractor, 'get_total_tokens') or not callable(self.extractor.get_total_tokens):
            raise ValueError("Extractor must have a 'get_total_tokens' method")

    async def extract_questions(self, image_paths: list[str]) -> list[str]:
        result = await self.extractor.send_request(image_paths)
        if isinstance(result,str):
            result = json.loads(result)
        logger.info(f"These are the results from the initial extraction {result} type {type(result)}")
        all_questions = self.parser(result)
        return all_questions

    async def create_multiple_prompts(self, image_paths: list[str]) -> list[str]:
        all_questions = await self.extract_questions(image_paths)
        return [self.base_prompt + question for question in all_questions]

    async def generate_multiple_ui(self, image_paths: list[str], outer_div_class: str) -> str:
        prompts: list[str] = await self.create_multiple_prompts(image_paths)
        logger.info(f"These are the the prompts of generating multiple ui {prompts}")
        if not prompts:
            logger.warning("There are no prompts will not generate valid ui")
        
        results = await asyncio.gather(
            *[self.generate_ui(prompt, UI) for prompt in prompts]
        )
        total_html = "".join(results)
        soup = BeautifulSoup(total_html, "html.parser")
        outer_div = soup.find("div")
        if outer_div:
            wrapper_div = soup.new_tag("section", **{"class": outer_div_class})
            outer_div.wrap(wrapper_div)
        return str(soup)

    def get_sum_tokens(self) -> int:
        # Get the total tokens from the extractor
        tokens_extractor = self.extractor.get_total_tokens()
        
        # Get the total tokens from the parent class
        parent_tokens = self.get_total_tokens()
        
        # Print the tokens for debugging or logging
        print(f"Tokens from extractor: {tokens_extractor}")
        print(f"Parent Tokens: {parent_tokens}")
        
        # Sum the tokens and store the result in total_tokens
        self.total_tokens = tokens_extractor + parent_tokens
        return self.total_tokens


# Define the LLM configuration with the specified model
llm_config = LLMConfig(
    api_key=api_key, 
    model="gpt-4o-mini", 
    temperature=0
)

# Define the image paths
image_paths = [
    r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\textbook_section\Screenshot 2024-08-21 191624.png"
]

# Initialize all the generators
conceptual_ui_generator = MultiUIContentGenerator(
    llm_config=llm_config,
    css_category="conceptual-question-section",
    base_prompt=conceptual_question_ui_prompt,
    extractor=extract_conceptual_questions,
    parser=conceptual_questions_parser
)

derivation_ui_generator = MultiUIContentGenerator(
    llm_config=llm_config,
    css_category="derivation-section",
    base_prompt=derivation_ui_prompt,
    extractor=extract_derivations,
    parser=derivations_parser
)

summary_ui_generator = MultiUIContentGenerator(
    llm_config=llm_config,
    css_category="summary_and_key_concepts",
    base_prompt=summary_ui_prompt,
    extractor=extract_summary,
    parser=lecture_summary_parser
)

async def main():
    # Run all the generators concurrently using asyncio.gather
    # derivation_html, conceptual_html, lecture_ui = await asyncio.gather(
    #     derivation_ui_generator.generate_multiple_ui(image_paths, "derivation-section")
    #     # conceptual_ui_generator.generate_multiple_ui(image_paths, "conceptual-question-section"),
    #     # summary_ui_generator.generate_multiple_ui(image_paths, "summary-section")
    # )
    derivation_html = await derivation_ui_generator.generate_multiple_ui(image_paths, "derivation-section")
        # conceptual_ui_generator.generate_multiple_ui(image_paths, "conceptual-question-section"),
        # summary_ui_generator.generate_multiple_ui(image_paths, "summary-section")
    
    
    # Print the generated HTML
    # print(lecture_ui)
    # print(conceptual_html)
    print(derivation_html)
    
    # Get the total tokens for each generator
    derivation_tokens = derivation_ui_generator.get_sum_tokens()
    # conceptual_tokens = conceptual_ui_generator.get_sum_tokens()
    # lecture_tokens = summary_ui_generator.get_sum_tokens()

    # Print token counts
    # print(f"These are the total tokens from the derivation class: {derivation_tokens}")
    # print(f"These are the total tokens from the conceptual class: {conceptual_tokens}")
    # print(f"These are the total tokens from the lecture class: {lecture_tokens}")
    # print(f"These are the total tokens: {derivation_tokens + conceptual_tokens + lecture_tokens}")

if __name__ == "__main__":
    asyncio.run(main())
