# import asyncio
# import tempfile
# from typing import Union,List
# import os
# from ..llm_content_assembly.utils import convert_pdf_to_images, is_image_file_extension
# from ..llm_generators.image_extraction.extract_computational_questions import computational_question_extraction_images
# from ..gestalt_module_generator.map_extracted_computational_questions import map_extracted_computational_questions

# import tempfile
# from typing import Union, List, Dict, Any
# import logging

# async def extract_question_images_user_uploaded(user_input: Union[List[str], str]) -> List[Dict[str, Any]]:
#     """
#     Extracts computational questions and their solutions from user-uploaded images or PDF files.

#     Args:
#         user_input (Union[List[str], str]): Either a list of image/PDF paths or a single PDF path uploaded by the user.

#     Returns:
#         List[Dict[str, Any]]: A list of dictionaries where each dictionary represents a question and its corresponding solution.
#     """
#     question_solution_pairs = []

#     # If the input is a list of image paths
#     if isinstance(user_input, list) and all(is_image_file_extension(file) for file in user_input):
#         print(f"\n this is the user input {user_input}\n")
#         result = await computational_question_extraction_images(user_input)
#         print(f"\n This is inside the extract question upload thing {result}\n this is the total length {len(result)} \n this is the type {type(result)}")
#         question_solution_pairs.extend(map_extracted_computational_questions(result))

#     # If the input is a single PDF path
#     elif isinstance(user_input, str) and not is_image_file_extension(user_input):
#         with tempfile.TemporaryDirectory() as tmpdir:
#             image_paths = convert_pdf_to_images(user_input, tmpdir)
#             result = await computational_question_extraction_images(image_paths)
#             question_solution_pairs.extend(map_extracted_computational_questions(result))

#     # If the input is a list of PDF paths
#     elif isinstance(user_input, list) and all(not is_image_file_extension(file) for file in user_input):
#         with tempfile.TemporaryDirectory() as tmpdir:
#             for pdf_path in user_input:
#                 image_paths = convert_pdf_to_images(pdf_path, tmpdir)
#                 result = await computational_question_extraction_images(image_paths)
#                 question_solution_pairs.extend(map_extracted_computational_questions(result))

#     # If the input is a list but contains a mix of images and non-image files
#     elif isinstance(user_input, list) and not all(is_image_file_extension(file) for file in user_input):
#         logging.error("The list contains a mix of image and non-image files.")
#         raise ValueError("The list contains a mix of image and non-image files.")

#     else:
#         logging.error("Invalid input type or file format.")
#         raise ValueError("Invalid input type or file format.")

#     return question_solution_pairs



# async def main():
#     # Uncomment and modify these inputs if needed
#     # input1 = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\test_images\Lecture_01_09.pdf"
#     input2 = [
#         r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\test_images\textbook_section\Screenshot 2024-08-21 191610.png"
#     ]
#     # input3 = [
#     #     r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\test_images\Lecture_01_09.pdf",
#     #     r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\test_images\Lecture_01_11.pdf"
#     # ]

#     # Define the folder path containing images
#     folder_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\test_images\textbook_section"
    
#     # List to store image paths
#     image_paths = []

#     # Walk through the directory to collect all image file paths
#     for root, dirs, files in os.walk(folder_path):
#         for file in files:
#             filepath = os.path.join(root, file)
#             image_paths.append(filepath)
    
#     # Print the collected image paths for debugging
#     print("Collected Image Paths:")
#     print(image_paths)
    
#     # Processing the images
#     print("Processing the collected images...")
#     result1 = await extract_question_images_user_uploaded(image_paths)
    
#     # Display the results
#     print(f"Result:\n{result1}\n{'-'*40}\n")
#     for result in result1:
#         print(f"Extracted Question: {result.get('question')}")
    
#     # Uncomment and modify these sections to process additional inputs
#     # print("Processing Input 2: List of Image Files")
#     # result2 = await extract_question_images_user_uploaded(input2)
#     # print(f"Result for Input 2:\n{result2}\n{'-'*40}\n")
    
#     # print("Processing Input 3: List of PDF Files")
#     # result3 = await extract_question_images_user_uploaded(input3)
#     # print(f"Result for Input 3:\n{result3}\n{'-'*40}\n")

# if __name__ == "__main__":
#     asyncio.run(main())