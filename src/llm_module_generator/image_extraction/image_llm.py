import os
import json
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain import hub
from .utils import create_image_content_payload

# Note
# This is a common method to get the prompt str prompt.messages[0].prompt.template
@dataclass
class ImageLLMProcessor:
    prompt:str
    response: BaseModel
    model:str

    def __post_init__(self):
        self.llm = ChatOpenAI(model=self.model)

    async def send_request(self, image_paths:list[str]):
        image_contents = await create_image_content_payload(image_paths)
        message = HumanMessage(
        content=[
            {"type": "text", "text": self.prompt.messages[0].prompt.template}, # type: ignore
            *image_contents,
        ],)
        response = await self.llm.with_structured_output(self.response).ainvoke([message]) # type: ignore
        return response.dict() # type: ignore





class KeyWord(BaseModel):
    keyword:str = Field(...,description="Keyword")
    description: str = Field(...,description = "Description of the keyword.Use LaTeX for any mathematical symbols or equations. ")
class LectureSummary(BaseModel):
    lecture_name: str = Field(...,description = "A concise and descriptive title of the lecture")
    lecture_subtitle: str= Field (...,description = "A subtitle that is essentially a super consise summary meant to add more information about the general lecture")
    summary: str = Field(..., description="A summary of the lecture material, describing the essence of what the lecture was about. Use LaTeX for any mathematical symbols or equations.")
    key_concepts: List[KeyWord] = Field(..., description="A list of key concepts covered in the lecture. Use LaTeX for any mathematical symbols or equations.")
    foundational_concepts: List[KeyWord] = Field(..., description="A list of prerequisite concepts that the lecture builds upon. Use LaTeX for any mathematical symbols or equations.")
    search_keywords: List[str] = Field(..., description="Return a list of relevant search queries which will be used to find external references for generating additional info", max_items=3)
class LectureAnalysis(BaseModel):
    analysis: LectureSummary = Field(..., description="The analysis of the lecture material.")
class Step(BaseModel):
    step_description: str = Field(..., description="An explanation of the step involved in solving the problem, using LaTeX for any mathematical symbols or equations.")
class ImageReq(BaseModel):
    requires_image: bool = Field(..., description="Indicate whether the question requires an image to solve.")
    image_description: Optional[str] = Field(None, description="If the question requires an image to solve, provide a description of the image that is needed.")
class ExternalDataReq(BaseModel):
    requires_external_data: bool = Field(..., description="Indicates whether external data, such as tabular data or charts, is needed to solve the question.")
    external_data: Optional[str] = Field(None, description="If external data is required, indicate the required data.")


class ComputationalQuestion(BaseModel):
    question: str = Field(..., description="A computational question that requires computation. Format any mathematical symbols or equations using LaTeX.")
    solution: Optional[List[Step]] = Field(default_factory=list, description="A detailed solution with steps for the computational question, using LaTeX for formatting any mathematical symbols or equations. This field is optional and defaults to an empty list if no solution is provided.")
    source: str = Field(..., description="The source from which this question is derived.")
    complete: bool = Field(..., description="Indicates if the computational question is completed with the solutions. If `false`, the `solution` field can be an empty list.")
    image_req: List[ImageReq] = Field(..., description="A list of image requirements for understanding the question, if any.")
    external_data_req: ExternalDataReq
 
class ExtractedCompuationalQuestions(BaseModel):
    extracted_question: List[ComputationalQuestion] = Field(...,description="A list of all the extracted questions")

class ImageRequirements(BaseModel):
    requires_image: str = Field(..., description="Indicates if the derivation requires an image to fully understand the derivation. Should be 'True' or 'False'.")
    recommended_image: str = Field(..., description="If the image is required, provide a recommendation of what the image should depict.")
class SingleDerivation(BaseModel):
    derivation_name: str = Field(..., description="The name of the derivation and what it aims to demonstrate.")
    derivation_steps: List[Step] = Field(..., description="A list of steps involved in the derivation, each step explained and formatted using LaTeX for mathematical symbols or equations.")
    derivation_source: str = Field(..., description="The source from which this derivation is derived.")
    image_stats: List[ImageRequirements] = Field(..., description="A list of image requirements for understanding the derivation, if any.")
class DerivationResponse(BaseModel):
    derivations: List[SingleDerivation] = Field(..., description="A list of derivations, each containing its name, steps, source, and image requirements if applicable.")


class ConceptualQuestion(BaseModel):
    question: str = Field(..., description="A conceptual question based on the lecture material that does not require any computation. Format any mathematical symbols or equations using LaTeX.")
    multiple_choice_options: List[str] = Field(..., description="Four multiple-choice options for the conceptual question. Format any mathematical symbols or equations using LaTeX.")
    correct_answer: str = Field(..., description="The correct option from the multiple-choice options. Format any mathematical symbols or equations using LaTeX.")
    source: str = Field(..., description="The source from which this question is derived.")
    generated: bool = Field(..., description="Whether the question was generated or extracted from the lecture material.")
class Questions(BaseModel):
    questions: List[ConceptualQuestion] = Field(..., description="A list of conceptual questions based on the lecture material.")


extract_summary = ImageLLMProcessor(
    prompt = hub.pull("lecture-summary"),
    response = LectureAnalysis,
    model = "gpt-4o"
)
extract_computational_questions = ImageLLMProcessor(
    prompt = hub.pull("extract-computational-questions"),
    response = ExtractedCompuationalQuestions,
    model = "gpt-4o"
)
extract_derivations = ImageLLMProcessor(
    prompt = hub.pull("extract-derivations"),
    response = DerivationResponse,
    model = "gpt-4o"
)
extract_conceptual_questions = ImageLLMProcessor(
    prompt = hub.pull("generate-conceptual-questions"),
    response = Questions,
    model = "gpt-4o"
)
# Helper Function Just sends request
async def process_with_extractor(extractor: ImageLLMProcessor, image_paths: List[str]) -> dict:
    return await extractor.send_request(image_paths=image_paths)


async def main(image_paths: List[str], prompt: str, response_format: Dict = None) -> tuple[Dict, int]:
    """
    Main function to fetch and return the structured response from images using multiple extractors.

    Args:
        image_paths (List[str]): A list of paths to the images to be processed.
        prompt (str): The prompt to send along with the images.
        response_format (Dict): The expected format of the response (optional).

    Returns:
        Tuple[Dict, int]: A tuple containing the structured response and the total token count.
    """
    extractors = [
        extract_summary,
        extract_computational_questions,
        extract_derivations,
        extract_conceptual_questions
    ]

    tasks = [asyncio.create_task(process_with_extractor(extractor, image_paths)) for extractor in extractors]
    results_list = await asyncio.gather(*tasks)
    return results_list

if __name__ == "__main__":
    async def run():
        try:
            print("Please enter the absolute path to the image file:")
            image_path = input().strip()

            # Validate the provided path
            if not os.path.isabs(image_path):
                raise ValueError("The provided path is not an absolute path.")
            if not os.path.isfile(image_path):
                raise FileNotFoundError(f"No file found at {image_path}. Please provide a valid image file path.")

            image_paths = [image_path]
            prompt = "Extract all the questions. Return as JSON structure."

            print("Processing the image and sending the request. Please wait...")
            results = await main(image_paths=image_paths, prompt=prompt)

            print("\nRequest completed successfully. Here is the result:")
            for result in results:
                print(f"\n{result}\n")


        except ValueError as ve:
            print(f"Value Error: {ve}")
        except FileNotFoundError as fnfe:
            print(f"File Not Found Error: {fnfe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    asyncio.run(run())