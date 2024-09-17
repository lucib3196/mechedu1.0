import asyncio
from typing import List, Tuple

from numpy import imag

from .file_converter import FileConverter
from .llm_lecture_processor import analyze_lecture
from .generate_module import generate_module_from_question
from ..logging_config.logging_config import get_logger
from ..llm_module_generator.parsers.parser import computational_question_parser
from ..llm_module_generator.image_extraction.image_llm_extraction import extract_computational_questions

# Initialize the logger
logger = get_logger(__name__)

# User data for module generation
user_data = {
    "created_by": "lberm007@ucr.edu",
    "code_language": "javascript"
}

async def lecture_assembly(paths: List[str], user_data:dict) -> Tuple[str, List[str], int]:
    """
    Processes lecture files and generates the necessary outputs.

    Args:
        paths (List[str]): List of file or directory paths to process.

    Returns:
        Tuple[str, List[str], int]: A tuple containing the main result, all modules generated, and the total token count.
    """
    tokens = 0
    file_manager = FileConverter()
    
    # Convert the input files to images
    image_paths = file_manager.convert_files_images(paths)
    print(f"These are the image paths {image_paths}")
    
    # Analyze the lecture images and generate the result, modules, and token count
    result, all_mod, tokens = await analyze_lecture(image_paths)
    html_module = ("lecture", {"lecture.html": result})
    all_mod.append([html_module])
    return all_mod,tokens

async def generate_module_text(question: str, user_data: dict) -> Tuple[List[Tuple[str, str]], int]:
    """
    Generates a module from a given question using user data.

    Args:
        question (str): The question text to generate the module from.

    Returns:
        Tuple[List[Tuple[str, str]], int]: A list of generated modules and the token count.
    """
    tokens = 0
    result = await generate_module_from_question(question, user_data=user_data)
    modules = []
    
    question_title = result.get("question_title", "")
    content = result.get("generated_content", "")
    tokens += result.get("mod_tokens")
    modules.append((question_title, content))

    logger.info(f"Finished generating module from text, total tokens {tokens}")
    return modules, tokens

async def generate_from_image(paths: List[str] ,user_data: dict) -> Tuple[List[Tuple[str, str]], int]:
    """
    Extracts computational questions from images and generates corresponding modules.

    Args:
        paths (List[str]): List of file or directory paths to process.

    Returns:
        Tuple[List[Tuple[str, str]], int]: A list of generated modules and the token count.
    """
    total_tokens = 0
    
    # Initialize the file converter
    file_manager = FileConverter()
    
    # Convert the input files to images
    image_paths = file_manager.convert_files_images(paths)

    logger.info("Extracting computational questions ...\n")
    
    # Extract computational questions from images
    computational_question_images = await extract_computational_questions.send_request(image_paths)
    computational_questions = computational_question_parser(response=computational_question_images)
    
    # Track token usage
    total_tokens += extract_computational_questions.get_total_tokens()

    # Generate modules from extracted questions
    results = await asyncio.gather(*[
        generate_module_from_question(
            comp_question.get("question"), 
            user_data, 
            solution_guide=comp_question.get("solution")
        ) 
        for comp_question in computational_questions
    ])

    # Compile modules
    modules = []
    for result in results:
        question_title = result.get("question_title", "")
        content = result.get("generated_content", "")
        total_tokens += result.get("mod_tokens")
        modules.append((question_title, content))

    logger.info("Finished extracting computational questions")
    return modules, total_tokens

async def main():
    # Placeholder paths (replace with actual paths)
    text_question = "A ball is traveling at a speed of 5m/s for a total time of 30 minutes. What is the total distance traveled"
    image_paths = [r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\textbook_section\Screenshot 2024-08-21 191610.png", r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\textbook_section\Screenshot 2024-08-21 191624.png"]
    lecture_paths = [r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\Lecture_01_09.pdf"]

    # # Run the text-based module generation
    # print("Running text-based module generation...")
    # text_modules, text_tokens = await generate_module_text(text_question)
    # print(f"Text-based module generation completed. Tokens used: {text_tokens}")
    # for module in text_modules:
    #     print(f"Module: {module}")

    # # Run the image-based module generation
    # print("\nRunning image-based module generation...")
    # image_modules, image_tokens = await generate_from_image(image_paths,user_data)
    # print(f"Image-based module generation completed. Tokens used: {image_tokens}")
    # for module in image_modules:
    #     print(f"Module: {module}")

    # Run the lecture assembly
    print("\nRunning lecture assembly...")
    lecture_result, all_modules, lecture_tokens = await lecture_assembly(lecture_paths,user_data=user_data)
    print(f"Lecture assembly completed. Tokens used: {lecture_tokens}")
    print(f"Lecture result: {lecture_result}")
    for module in all_modules:
        print(f"Module: {module}")

if __name__ == "__main__":
    asyncio.run(main())