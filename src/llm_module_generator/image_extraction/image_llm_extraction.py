import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import os
from .image_extraction_prompts import (
    conceptual_question_prompt,
    lecture_analysis_prompt,
    extract_derivations_prompt,
    extract_computation_questions_prompt,
)
from .image_llm_processor import ImageToLLMProcessor



class LectureSummary(BaseModel):
    summary: str = Field(..., description="A summary of the lecture material, describing the essence of what the lecture was about. Use LaTeX for any mathematical symbols or equations.")
    key_concepts: List[str] = Field(..., description="A list of key concepts covered in the lecture. Use LaTeX for any mathematical symbols or equations.")
    keywords: List[str] = Field(..., description="A list of keywords that describe the lecture. Use LaTeX for any mathematical symbols or equations.")
    foundational_concepts: List[str] = Field(..., description="A list of prerequisite concepts that the lecture builds upon. Use LaTeX for any mathematical symbols or equations.")


class LectureAnalysis(BaseModel):
    analysis: LectureSummary = Field(..., description="The analysis of the lecture material.")


class Step(BaseModel):
    explanation: str = Field(..., description="An explanation of the step involved in solving the problem, using LaTeX for any mathematical symbols or equations.")
    output: str = Field(..., description="The output or result of the step, formatted in LaTeX if it includes any mathematical symbols or equations.")


class ImageReq(BaseModel):
    requires_image: bool = Field(..., description="Indicate whether the question requires an image to solve.")
    image_description: Optional[str] = Field(None, description="If the question requires an image to solve, provide a description of the image that is needed.")


class ExternalDataReq(BaseModel):
    requires_external_data: bool = Field(..., description="Indicates whether external data, such as tabular data or charts, is needed to solve the question.")
    external_data: Optional[str] = Field(None, description="If external data is required, indicate the required data.")


class ComputationalQuestion(BaseModel):
    question: str = Field(..., description="A computational question that requires computation. Format any mathematical symbols or equations using LaTeX.")
    solution: Optional[List[Step]] = Field(None, description="A detailed solution with steps for the computational question, using LaTeX for formatting any mathematical symbols or equations. This field is optional and should be `None` if a solution is not present, particularly if the `complete` field is `false`.")
    source: str = Field(..., description="The source from which this question is derived.")
    complete: bool = Field(..., description="Indicates if the computational question is completed with the solutions. If `false`, the `solution` field can be `None`.")
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


# Define the JSON schemas
lecture_schema = LectureAnalysis.model_json_schema()
computational_schema = ExtractedCompuationalQuestions.model_json_schema()
derivation_schema = DerivationResponse.model_json_schema()
conceputual_question_schema = Questions.model_json_schema()

## Define all the extractors
extract_summary = ImageToLLMProcessor(prompt=lecture_analysis_prompt,response_schema=lecture_schema)
extract_computational_questions = ImageToLLMProcessor(prompt=extract_computation_questions_prompt,response_schema=computational_schema)
extract_derivations = ImageToLLMProcessor(prompt = extract_derivations_prompt, response_schema = derivation_schema)
extract_conceptual_questions = ImageToLLMProcessor(prompt = conceptual_question_prompt, response_schema = conceputual_question_schema)


async def process_with_extractor(extractor: ImageToLLMProcessor, image_paths: List[str]) -> dict:
    """
    Process the images using the specified extractor and return the structured response.

    Args:
        extractor (ImageToLLMProcessor): The extractor instance to process the images.
        image_paths (List[str]): A list of paths to the images to be processed.
        prompt (str): The prompt to send along with the images.

    Returns:
        dict: The structured response obtained from the images.
    """
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

    total_tokens = sum(extractor.get_total_tokens() for extractor in extractors)


    return results_list, total_tokens

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
            results, token_count = await main(image_paths=image_paths, prompt=prompt)

            print("\nRequest completed successfully. Here is the result:")
            for result in results:
                print(f"\n{result}\n")
            print(f"Total tokens used: {token_count}")

        except ValueError as ve:
            print(f"Value Error: {ve}")
        except FileNotFoundError as fnfe:
            print(f"File Not Found Error: {fnfe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    asyncio.run(run())