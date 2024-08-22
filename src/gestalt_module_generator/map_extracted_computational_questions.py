import logging
from typing import List, Dict

def map_extracted_computational_questions(response: Dict) -> List[Dict[str, str]]:
    """
    Maps extracted computational questions and their solutions from the provided response.

    This function takes a response dictionary containing extracted questions and their details, checks if each 
    question is complete, and constructs a corresponding solution guide. It returns a list of dictionaries where 
    each dictionary represents a question and its corresponding solution.

    Args:
        response (Dict): The dictionary containing extracted questions and their details. The expected format 
                         includes keys like 'extracted_question', 'question', 'complete', 'solution', 'image_req', 
                         and 'external_data_req'.

    Returns:
        List[Dict[str, str]]: A list of dictionaries where each dictionary represents a question and its corresponding solution.
    """
    question_solution_pairs = []

    # Extract the list of questions from the response
    extracted_questions = response.get("extracted_question", [])

    # Iterate over each extracted question
    for extracted_question in extracted_questions:
        question_text = extracted_question.get("question")
        
        if question_text:
            # Check if the question is marked as complete
            is_complete = extracted_question.get("complete", False)
            
            if is_complete:
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
                logging.warning(f"Question '{question_text}' is incomplete or missing solutions.")
        else:
            logging.warning("No question found in the extracted data.")

    return question_solution_pairs
