# from src.llm_generators.conceptual_question_extraction_images import conceptual_question_extraction_images
# from src.llm_generators.generate_conceptual_question_html import generate_conceptual_questions_html
# # from src.llm_generators.computational_question_extraction_images  import computational_question_extraction_images
# from src.llm_generators.extract_derivations_image import extract_derivations_image
# from src.llm_generators.generate_derivations_html import generate_derivations_html
# from src.llm_generators.extract_summary_key_concepts_image import extract_summary_and_key_concepts_image
# from src.llm_generators.generate_lecture_summary_html import generate_lecture_summary_html
# from src.llm_generators.lecture_triaging_agent import lecture_triaging_agent
# import asyncio
# import os
# from typing import List
# from time import time
# from dataclasses import dataclass


# # Step 1: Define the functions
# async def extract_summary_and_key_concepts(image_paths:List[str]):
#     print("Extracting summary and key concepts...\n")
#     response = await extract_summary_and_key_concepts_image(image_paths=image_paths)
#     html = await generate_lecture_summary_html(response)
#     print("Finished extracting summary and key concepts.")
#     return html

# async def conceptual_question_extraction(image_paths:List[str]):
#     print("Extracting conceptual questions from images...")
#     response = await conceptual_question_extraction_images(image_paths=image_paths)
#     html = await generate_conceptual_questions_html(response)
#     print("Finished extracting conceptual questions from images.")
#     return html

# async def extract_derivations(image_paths:List[str]):
#     print("Extracting derivations from images...\n")
#     response = await extract_derivations_image(image_paths)
#     html = await generate_derivations_html(response)
#     return html

# async def computational_question_extraction(image_paths:List[str]):
#     print("Extracting computational questions from images...\n")
#     await asyncio.sleep(1)
#     print("Finished extracting conceptual questions from images.")
#     return f"Finished"
    
# async def analyze_lecture(image_paths: List[str]):
#     """
#     Analyze lecture images by calling the appropriate functions determined by the triaging agent.
    
#     Args:
#         image_paths (List[str]): A list of paths to the lecture images.
#     """
    
#     # Define the valid tools that can be used for analysis
#     valid_tools = [
#         "extract_summary_and_key_concepts", 
#         "conceptual_question_extraction",
#         "extract_derivations",
#         "computational_question_extraction"
#     ]

#     print("\nStarting Analysis\n")
    
#     # Determine which functions need to be called based on the lecture content
#     functions_to_execute = await lecture_triaging_agent(image_paths=image_paths)
#     print(f"Functions to be executed: {functions_to_execute}\n")
    
#     # Prepare and run the tasks concurrently
#     tasks = []
#     async with asyncio.TaskGroup() as task_group:
#         for function_name in functions_to_execute:
#             if function_name in globals():  # Check if the function is globally available
#                 function_to_call = globals()[function_name]
#                 task = task_group.create_task(function_to_call(image_paths), name=function_name)
#                 tasks.append(task)
    
#     # Store the results in a dictionary, using function names as keys
#     analysis_results = {}
#     for task in tasks:
#         task_name = task.get_name()
#         analysis_results[task_name] = {
#             "output": task.result(),
#         }

#     # Print the results of the analysis
#     print(analysis_results)
    
#     htmls = []
#     # Handle and print the output for each specific function, if executed
#     if analysis_results.get("extract_summary_and_key_concepts"):
#         print("Summary and Key Concepts Output:")
#         htmls.append(analysis_results["extract_summary_and_key_concepts"]["output"])
    
#     if analysis_results.get("conceptual_question_extraction"):
#         print("Conceptual Questions Output:")
#         htmls.append(analysis_results["conceptual_question_extraction"]["output"])
    
#     if analysis_results.get("extract_derivations"):
#         print("Derivations Output:")
#         htmls.append(analysis_results["extract_derivations"]["output"])
    
#     if analysis_results.get("computational_question_extraction"):
#         print("Computational Questions Output:")
#         print(analysis_results["computational_question_extraction"]["output"])
    
#     result = f"<body>{''.join(str(html) for html in htmls)}</body>"

#     with open('my_page.html', 'w') as file:
#         file.write(result)
#     return None
        

# async def main():
#     start_time = time()
#     current_dir = os.getcwd()
#     image_location = r"mechedu1.0\test_images\lecture_18"
#     image_location_single = r"mechedu1.0\test_images\textbook_ex1.png"
    
    
#     # Construct the full path for the single image
#     image_paths_single = os.path.join(current_dir, image_location_single)
    
#     # Construct the full paths for all images in the directory
#     image_paths_directory = [os.path.join(current_dir, image_location, file) 
#                              for _, _, files in os.walk(image_location) for file in files]
    
#     # Process images in the directory
#     print(f"\n Processing the following image paths from the directory: {image_paths_directory} \n")
#     result = await analyze_lecture(image_paths=image_paths_directory)
#     print(result)
#     # Process the single image
#     print(f"\n Processing the single image path: {image_paths_single} \n")
#     # result = await analyze_lecture(image_paths=[image_paths_single])
#     # print(result)
#     end_time = time()
#     total_time = end_time-start_time
#     print(f"Total Time For Generation {total_time} seconds")
    
    
# if __name__ == "__main__":
#     result = asyncio.run(main())
