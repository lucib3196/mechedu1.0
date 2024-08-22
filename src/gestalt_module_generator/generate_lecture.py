import asyncio
import os
from typing import List,Union
from time import time
from dataclasses import dataclass
import tempfile
from ..llm_generators.agent.lecture_triaging_agent import lecture_triaging_agent
from ..llm_generators.generate_ui.generate_lecture_summary_ui import generate_lecture_summary_html
from ..llm_generators.generate_ui.generate_derivations_html import generate_derivations_html
from ..llm_generators.generate_ui.generate_conceptual_question_html import generate_conceptual_questions_html, extract_conceptual_questions

from ..llm_generators.image_extraction.extract_summary_images import extract_summary_and_key_concepts_image
from ..llm_generators.image_extraction.extract_computational_questions import computational_question_extraction_images
from ..llm_generators.image_extraction.conceputual_question_extraction_images import conceptual_question_extraction_images
from ..llm_generators.image_extraction.extract_derivations_images import extract_derivations_image
from ..gestalt_module_generator.generate_gestalt_module import generate_module
from ..gestalt_module_generator.utils import is_image_file_extension,convert_pdf_to_images
from ..gestalt_module_generator.extract_question_images import extract_question_images_user_uploaded
user_data =  user_data = {
        "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
        "code_language": "javascript",
    }
# Step 1: Define the functions
async def extract_summary_and_key_concepts(image_paths:List[str]):
    print("Extracting summary and key concepts...\n")
    response = await extract_summary_and_key_concepts_image(image_paths=image_paths)
    html = await generate_lecture_summary_html(response)
    print("Finished extracting summary and key concepts.")

    return html

async def conceptual_question_extraction(image_paths: List[str]):
    print("Extracting conceptual questions from images...")

    # Extract conceptual questions from images
    response = await conceptual_question_extraction_images(image_paths=image_paths)
    conceptual_questions = extract_conceptual_questions(response)

    # Create a list of tasks for generating modules concurrently
    generate_modules_tasks = [asyncio.create_task(generate_module(question,user_data)) for question in conceptual_questions]

    # Run the generate_conceptual_questions_html concurrently without waiting for modules to be generated
    html_task = asyncio.create_task(generate_conceptual_questions_html(response))

    # Await the completion of module generation tasks (modules will be generated in the background)
    generated_modules = await asyncio.gather(*generate_modules_tasks)
    # generated_modules
    # Await the HTML generation task (this runs concurrently with the module generation)
    html = await html_task

    print("Finished extracting conceptual questions from images.")
    return html,generated_modules

async def extract_derivations(image_paths:List[str]):
    print("Extracting derivations from images...\n")
    response = await extract_derivations_image(image_paths)
    html = await generate_derivations_html(response)
    return html

async def computational_question_extraction(image_paths:List[str]):
    print("Extracting computational questions from images...\n")
    
    generated_content = await generate_module(image_paths,user_data=user_data)
    print("Finished extracting conceptual questions from images.")
    return generated_content


async def analyze_lecture(image_paths: List[str]):
    """
    Analyze lecture images by calling the appropriate functions determined by the triaging agent.
    
    Args:
        image_paths (List[str]): A list of paths to the lecture images.
    """
    
    # Define the valid tools that can be used for analysis
    print("\nStarting Analysis\n")
    
    # Determine which functions need to be called based on the lecture content
    functions_to_execute = await lecture_triaging_agent(image_paths=image_paths)
    print(f"Functions to be executed: {functions_to_execute}\n")
    
    # Prepare and run the tasks concurrently
    tasks = []
    async with asyncio.TaskGroup() as task_group:
        for function_name in functions_to_execute:
            if function_name in globals():  # Check if the function is globally available
                function_to_call = globals()[function_name]
                task = task_group.create_task(function_to_call(image_paths), name=function_name)
                tasks.append(task)
    
    # Store the results in a dictionary, using function names as keys
    analysis_results = {}
    for task in tasks:
        task_name = task.get_name()
        analysis_results[task_name] = {
            "output": task.result(),
        }

    # Print the results of the analysis
    print(analysis_results)
    
    htmls = []
    all_modules = []
    # Handle and print the output for each specific function, if executed
    if analysis_results.get("extract_summary_and_key_concepts"):
        print("Summary and Key Concepts Output:")
        htmls.append(analysis_results["extract_summary_and_key_concepts"]["output"])
    
    if analysis_results.get("conceptual_question_extraction"):
        print("Conceptual Questions Output:")
        results = analysis_results["conceptual_question_extraction"]["output"]
        html, generated_modules = results
        htmls.append(html)
        all_modules.extend(generated_modules)
    
    if analysis_results.get("extract_derivations"):
        print("Derivations Output:")
        htmls.append(analysis_results["extract_derivations"]["output"])
    
    if analysis_results.get("computational_question_extraction"):
        print("Computational Questions Output:")
        generated_modules = analysis_results["computational_question_extraction"]["output"]
        all_modules.extend(generated_modules)
    
    result = f"<body>{''.join(str(html) for html in htmls)}</body>"

    # with open('my_page.html', 'w') as file:
    #     file.write(result)
    return result,all_modules


async def process_lecture_content(user_input: Union[str, List[str]], user_data: dict):
    """
    Processes lecture content by analyzing images or converting PDFs to images before analysis.
    """

    # Determine if input files are images or PDFs
    if not all(is_image_file_extension(file) for file in user_input):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert PDFs to images and store the paths in a temporary directory
            image_paths = [convert_pdf_to_images(file, temp_dir) for file in user_input]
            # Analyze the first set of images
            generated_html, module_content = await analyze_lecture(image_paths=image_paths[0])
    else:
        image_paths = []
        
        # Collect image paths from directories or single files
        for path in user_input:
            if os.path.isdir(path):
                # Add all image files from the directory to the image_paths list
                directory_images = [
                    os.path.join(path, file) 
                    for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))
                ]
                image_paths.extend(directory_images)
            elif os.path.isfile(path):
                # Add the single image file to the image_paths list
                image_paths.append(path)
            else:
                # Print an error message if the path is invalid and exit
                print(f"Provided path does not exist: {path}")
                return
        
        # If no valid images were found, exit with an error message
        if not image_paths:
            print("No valid image paths provided.")
            return

        # Print the image paths being processed
        print(f"\nProcessing the following image paths: {image_paths}\n")
        # Analyze the collected images
        generated_html, module_content = await analyze_lecture(image_paths=image_paths)

    # Save the generated HTML content as part of the module
    html_module = ("lecture", {"lecture.html": generated_html})
    module_content.append([html_module])
    
    # Print the processed modules for debugging purposes
    print("Processed modules:")
    print(module_content)

    # Return the content to be sent
    return module_content


async def main():
    """
    Main function to process lecture content from user-provided paths.
    """
    # Start timing the execution
    start_time = time()

    # Accept multiple absolute paths or a directory as input from the user
    absolute_paths_input = input("Please enter the absolute paths of files or directory, separated by commas: ").strip()
    
    # Split the input into a list of paths
    absolute_paths = [path.strip() for path in absolute_paths_input.split(',')]
    print(f"User provided paths: {absolute_paths}")

    # Example user data; modify as needed
    user_data = {
        "created_by": "user@example.com",  # Replace with actual user data
        "additional_info": "Additional information if needed"
    }

    # Call the function to process lecture content with the user input
    content_to_send = await process_lecture_content(user_input=absolute_paths, user_data=user_data)

    if content_to_send:
        # Print the returned content
        print("\nProcessed Content:\n")
        for content in content_to_send:
            print(content)

    # End timing the execution
    end_time = time()
    total_time = end_time - start_time
    print(f"\nTotal Time For Generation: {total_time:.2f} seconds")

# Example usage of the main function in an async context:
if __name__ == "__main__":
    asyncio.run(main())