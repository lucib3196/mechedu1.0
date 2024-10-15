from pydantic import BaseModel,Field
from typing import List
import asyncio
import os
import json
<<<<<<< HEAD
from ..image_extraction.image_llm import ImageLLMProcessor
from langchain import hub
=======
from ..image_extraction.image_llm_processor import ImageToLLMProcessor


triaging_system_prompt = """
You are responsible for assessing the user's query and analyzing the provided material. Route the query to the appropriate functions based on the content. The available functions are:

- **extract_summary_and_key_concepts**: This function is typically the default choice and should be used to extract the summary and key concepts when the material is formatted like a lecture. It should be called in most cases where the content is detailed and lecture-like.

- **conceptual_question_extraction**: This function is also generally a default choice, particularly when **extract_summary_and_key_concepts** is used. It complements the extraction by generating or identifying related conceptual questions. For shorter materials, such as collections of questions, apply the same conditions as for the **computational_question_extraction** function.

- **extract_derivations**:  This function should be called on a case-by-case basis, specifically when the material includes formal mathematical derivations. A derivation refers to a detailed, step-by-step explanation or proof that shows how a particular mathematical formula, equation, or result is derived. This function is most applicable when dealing with content related to physics or engineering subjects, where such detailed mathematical processes are often presented.

- **computational_question_extraction**: Like **extract_derivations**, this function is used on a case-by-case basis. It should be called when the material includes problems with solutions, ranging from single to multiple questions.

In most scenarios, **extract_summary_and_key_concepts** and **conceptual_question_extraction** are the primary functions to use, while **extract_derivations** and **computational_question_extraction** are more specialized and should be used based on specific content characteristics.

Forward the user's query to the relevant functions using the send_query_to_functions tool based on the material's content and format.

Additionally, provide an overall summary of the content you are analyzing. If possible, indicate how many pages or slides were provided and whether the material consists of a single page or multiple pages/slides.
"""
triaging_system_prompt_simple = """
You are responsible for assessing the user's query and analyzing the provided material. Route the query to the appropriate functions based on the content. The available functions are:

- **extract_summary_and_key_concepts**: This function must always be called to extract the summary and key concepts, especially when the material is formatted like a lecture. It should be used in all cases where the content is detailed and lecture-like, ensuring that the core ideas and concepts are captured.

- **conceptual_question_extraction**: This function should also always be called, complementing **extract_summary_and_key_concepts** by generating or identifying related conceptual questions. These two functions work together to ensure that the key points and related questions are clearly defined. For shorter materials, such as collections of questions, apply the same conditions as for the **computational_question_extraction** function.

- **extract_derivations**: This function must be used whenever the material contains any sort of formal proof or mathematical derivation. A derivation refers to a detailed, step-by-step explanation or proof that shows how a particular mathematical formula, equation, or result is derived. It is essential for handling content related to physics, engineering, or other subjects involving detailed mathematical processes.

In every scenario, **extract_summary_and_key_concepts** and **conceptual_question_extraction** should always be executed. **extract_derivations** should be used whenever there are any proofs, derivations, or step-by-step mathematical explanations.

Forward the user's query to the relevant functions using the send_query_to_functions tool based on the material's content and format.

Additionally, provide an overall summary of the content you are analyzing. If possible, indicate how many pages or slides were provided and whether the material consists of a single page or multiple pages/slides.
"""

>>>>>>> 582037f6b5e2c16b57d45240f86c66f7a690c6c4
class Response(BaseModel):
    functions_call: List[str] = Field(...,description="An array of functions to call")
    summary: str = Field("A consise summary of the content of the content provided ")
    pages: int = Field("A number of pages/slides you were given. This is meant to indicate how much content you were given")
<<<<<<< HEAD
lecture_triaging_agent = ImageLLMProcessor(    
    prompt = hub.pull("lecture-triaging"),
    response = Response,
    model = "gpt-4o-mini"
)
=======


agent_schema = Response.model_json_schema()


lecture_triaging_agent = ImageToLLMProcessor(triaging_system_prompt,agent_schema)
lecture_triaging_agent_simple = ImageToLLMProcessor(triaging_system_prompt_simple,agent_schema)
>>>>>>> 582037f6b5e2c16b57d45240f86c66f7a690c6c4


async def main():
    try:
        print("Please enter the absolute paths to the image files, separated by commas:")
        image_paths_input = input()
        
        # Split the input into a list of paths
        image_paths = [path.strip() for path in image_paths_input.split(',')]
        
        # Validate each provided path
        for image_path in image_paths:
            if not os.path.isabs(image_path):
                raise ValueError(f"The provided path '{image_path}' is not an absolute path.")
            if not os.path.isfile(image_path):
                raise FileNotFoundError(f"No file found at '{image_path}'. Please provide a valid image file path.")
        
        print(image_paths)
        print("Processing the images and sending the request. Please wait...")
        
        # Process the images using the lecture_triaging_agent
        result = await lecture_triaging_agent.send_request(image_paths)
        print(result)

    except ValueError as ve:
        print(f"Value Error: {ve}")
    except FileNotFoundError as fnfe:
        print(f"File Not Found Error: {fnfe}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())