
from ..image_extraction.image_llm_extraction import extract_computational_questions,extract_conceptual_questions,extract_derivations,extract_summary
import asyncio
from ...logging_config.logging_config import get_logger

logger = get_logger(__name__)

def conceptual_questions_parser(result: dict) -> list[str]:
    extracted_questions = result.get("questions","")
    all_questions = []
    for question in extracted_questions:
        question_text = f"Question: {question.get('question', 'Unknown')}"
        multiple_choice_options = question.get('multiple_choice_options', [])
        options_text = "\n".join(f" - Option: {option}" for option in multiple_choice_options)
        correct_answer = f"Correct Answer: {question.get('correct_answer', 'No answer provided')}"
        combined_text = f"{question_text}\n{options_text}\n{correct_answer}"
        all_questions.append(combined_text)
    return all_questions

def derivations_parser(response: dict) -> list[str]:
    derivations = response.get("derivations", [])
    all_derivations = []

    for derivation in derivations:
        # Extract derivation name
        derivation_name = f"Derivation Name: {derivation.get('derivation_name', 'Unknown')}"

        # Extract derivation steps, ensuring LaTeX backslashes are properly escaped
        derivation_steps = "\n".join(
            "- Explanation: " + step.get('explanation', 'No explanation provided').replace('\\', '\\\\') +  # Escaping LaTeX backslashes
            "\n  Step: " + step.get('output', 'No output provided').replace('\\', '\\\\')  # Escaping LaTeX backslashes
            for step in derivation.get("derivation_steps", [])
        )
        
        # Extract derivation source
        derivation_source = f"Derivation Source: {derivation.get('derivation_source', 'Unknown source')}"
        
        # Extract image stats
        image_stats = derivation.get("image_stats", [])
        if image_stats:
            requires_image = image_stats[0].get("requires_image", "False")
            recommended_image = image_stats[0].get("recommended_image", "No recommended image")
            image_info = f"Requires Image: {requires_image}, Recommended Image: {recommended_image}"
        else:
            image_info = "No image information available."
        
        # Combine all extracted info
        derivation_info = f"{derivation_name}\n{derivation_steps}\n{derivation_source}\n{image_info}"
        all_derivations.append(derivation_info)

    return all_derivations




def lecture_summary_parser(response: dict) -> list[str]:
    analysis = response.get("analysis", {})
    if analysis:
        summary = analysis.get('summary', "No summary provided.")
        key_concepts_list = analysis.get('key_concepts', [])
        foundational_concepts_list = analysis.get('foundational_concepts', [])
    else:
        summary = response.get('summary', "No summary provided.")
        key_concepts_list = response.get('key_concepts', [])
        foundational_concepts_list = response.get('foundational_concepts', [])
        
    # Parsing key concepts
    key_concepts = "\n".join([
        f"- {concept}\n"
        for concept in key_concepts_list
    ]) or "No key concepts provided."

    # Parsing foundational concepts
    foundational_concepts = "\n".join(foundational_concepts_list) or "No foundational concepts provided."

    # Constructing the parsed summary
    parsed_summary = f"""
    **Summary of Lecture**: Create a section that provides a concise overview of the lecture's main points. Use appropriate headings and bullet points to make the content easily digestible.
    - Ensure every detail provided is included: Summary: {summary}

    **Key Concepts**: Highlight the essential concepts covered in the lecture. Clearly define each concept, and where applicable, accompany them with relevant examples or illustrations. Organize the content effectively using HTML elements like lists or tables.
    {key_concepts}

    **Foundational Concepts**: Detail the foundational concepts that underlie the lecture material. This section should thoroughly explain each concept and its relevance to the lecture's topic.
    - Include every piece of information provided: Foundational Concepts: {foundational_concepts}
    """

    return [parsed_summary]

def computational_question_parser(response: dict)->list[dict]:
    """
    Parses the response dictionary to extract computational questions and their corresponding solutions.

    Args:
        response (dict): A dictionary containing the extracted questions and their details.
                         The expected structure includes a list under the key "extracted_question",
                         where each entry is a dictionary with keys like "question", "complete", "solution",
                         "image_req", and "external_data_req".

    Returns:
        list: A list of dictionaries, where each dictionary represents a question and its solution.
              Each dictionary contains the following keys:
                  - "question" (str): The text of the question.
                  - "solution" (str): The solution guide, formatted as a string.
                  - "image_req" (str): Additional requirements for images, if any.
                  - "external_data_req" (str): External data requirements, if any.

    Raises:
        None: This function does not raise any exceptions directly, but it logs warnings for incomplete or missing data.

    Example:
        response = {
            "extracted_question": [
                {
                    "question": "What is the velocity of the object?",
                    "complete": True,
                    "solution": [{"explanation": "Using the formula...", "output": "v = 10 m/s"}],
                    "image_req": "velocity_diagram.png",
                    "external_data_req": ""
                }
            ]
        }
        result = computational_question_parser(response)
        print(result)
        # Output: [{'question': 'What is the velocity of the object?', 'solution': '\nUsing the formula...\nv = 10 m/s', 'image_req': 'velocity_diagram.png', 'external_data_req': ''}]
    """
    question_solution_pairs = []

    # Extract the list of questions from the response
    extracted_questions = response.get("extracted_question", [])
    print(extracted_questions)
    
    # Iterate over each extracted question
    for extracted_question in extracted_questions:
        question_text = extracted_question.get("question")
        
        if question_text:
            # Check if the question is marked as complete
            is_complete = extracted_question.get("complete", False)
            
            if not is_complete:
                logger.warning(f"Question '{question_text}' is incomplete or missing solutions may not produce desired results")

            solution_steps = extracted_question.get("solution", [])
            solution_guide = []

            # Construct the solution guide by iterating over each step in the solution
            for step in solution_steps:
                explanation = step.get('explanation', 'No explanation provided')
                output = step.get('output', 'No output provided')
                solution_guide.append(f"\n{explanation}\n{output}")

            # Map the question and its corresponding details
            question_mapping = {
                "question": question_text,
                "solution": ''.join(solution_guide),
                "image_req": extracted_question.get("image_req", ""),
                "external_data_req": extracted_question.get("external_data_req", "")
            }
            
            # Add the question and solution to the list
            question_solution_pairs.append(question_mapping)
        else:
            logger.warning("No question found in the extracted data.")

    return question_solution_pairs



import asyncio

async def main():
    image_paths = [
        r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\test_images\textbook_section\Screenshot 2024-08-21 191523.png"
    ]
    
    # Send the request to extract computational questions

    comp_res, conc_res,der_res,sum_res = await asyncio.gather(
        extract_computational_questions.send_request(image_paths),
        extract_conceptual_questions.send_request(image_paths),
        extract_derivations.send_request(image_paths),
        extract_summary.send_request(image_paths)
    )
    print(sum_res)
    results = [
    computational_question_parser(comp_res),
    conceptual_questions_parser(conc_res),
    derivations_parser(der_res),
    lecture_summary_parser(sum_res)]
    for result in results:
        print(f"\nResult\n: {result}")

    computational_tokens = extract_computational_questions.get_total_tokens()
    conceptual_tokens = extract_conceptual_questions.get_total_tokens()
    derivation_tokens  = extract_derivations.get_total_tokens()
    lecture_tokens = extract_summary.get_total_tokens()

    print(f"These are the total tokens from the computational class: {computational_tokens}")
    print(f"These are the total tokens from the conceptual class: {conceptual_tokens}")
    print(f"These are the total tokens from the derivation class: {derivation_tokens}")
    print(f"These are the total tokens from the lecture class: {lecture_tokens}")
    # Print the total tokens used
    print(f"These are the total tokens: {derivation_tokens + conceptual_tokens + lecture_tokens+computational_tokens}")

if __name__ == "__main__":
    asyncio.run(main())
