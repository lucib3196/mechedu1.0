# from typing import Union, List,Dict,Any,Optional,Tuple
# from time import time
# import asyncio
# import json
# from .extract_question_images import extract_question_images_user_uploaded
# from .generate_gestalt_metadata import generate_module_metadata
# from ..gestalt_module_generator.generate_adaptive_module import process_adaptive_question
# from ..gestalt_module_generator.generate_nonadaptive_module import process_nonadaptive_question
# from ..llm_content_assembly.utils import is_image_file_extension,is_adaptive_question,extract_question_title


# async def generate_question_content(question: str, user_data: dict, solution_guide: str = None) -> Tuple[str, Dict]:
#     """
#     Generates content for a given question by determining whether it is adaptive or non-adaptive
#     and processing it accordingly.

#     Args:
#         question (str): The text of the question to be processed.
#         user_data (dict): A dictionary containing user-specific data that will be used to generate metadata.
#         solution_guide (str, optional): An optional guide providing solutions for the question. Defaults to None.

#     Returns:
#         Tuple[str, Dict]: A tuple containing the question title and a dictionary with the generated content.
#                          The generated content will vary based on whether the question is adaptive or non-adaptive.
#     """
#     metadata_dict = await generate_module_metadata(question, user_data)
#     question_title = extract_question_title(metadata_dict)
    
#     if is_adaptive_question(metadata_dict):
#         generated_content = await process_adaptive_question(question, metadata_dict, solution_guide)
#     else:
#         generated_content = await process_nonadaptive_question(question, metadata_dict)
    
#     return question_title, generated_content


# async def generate_module(user_input: Union[str, List[str]],user_data:dict):
#     if isinstance(user_input,str) and not is_image_file_extension(user_input):
#         question = user_input
#         results = [await generate_question_content(question=question, user_data=user_data)]
#     else:
#         image_data = await extract_question_images_user_uploaded(user_input)
#         tasks = []

#         for data in image_data:
#             question = data.get("question","")
#             solution_guide = data.get("solution","")
#             tasks.append(asyncio.create_task(generate_question_content(
#                 question=question,
#                 user_data=user_data,
#                 solution_guide=solution_guide,
#             )))
#         results = await asyncio.gather(*tasks)
#     for result in results:
#         question_title, module = result
#         print(f"This is the question title {question_title}\n Here is the generated module {module}\n")
#     return results

        
# if __name__ == "__main__" :
#     user_data = {
#         "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
#         "code_language": "javascript",
#     }
#     image_path = [r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\test_images\textbook_ex1.png"]
#     result = asyncio.run(generate_module(image_path,user_data))
#     print(result)