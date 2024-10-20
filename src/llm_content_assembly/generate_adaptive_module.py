import asyncio
from typing import Optional,Dict ,Any
from . import question_html_generator, question_solution_generator,server_js_generator,server_py_generator,question_solution_generator_flask
from . import get_logger
logger = get_logger(__name__)

async def generate_question_html(question: str,instructions:dict = {}) -> str:
    """
    Generates HTML content for the given question instructions.

    Args:
        question_instructions (str): Instructions for generating question HTML.

    Returns:
        str: Generated question HTML.
    """
    logger.info("Generating question HTML...")
    question_html_instructions = instructions.get("question_html_instructiosn")
    try:
        question_html = await question_html_generator.acall_generate_code(
            question,question_html_instructions
        )
        logger.info("Finished generating question HTML.")
        return question_html
    except Exception as e:
        logger.error(f"Failed to generate question HTML: {e}", exc_info=True)
        raise

async def generate_server_and_solution(
    question_html:str,
    instructions:Optional[dict]={}):
    server_instructions = instructions.get("server_instructions","")
    solution = instructions.get("solution_guide","")
    try: 
        logger.info("Generating server JS, server PY, and solution HTML concurrently.")
        logger.info(f"Solution Guide Provided for Code Generation {solution}")
        server_js_task = server_js_generator.acall_generate_code(question_html,server_instructions,solution)
        server_py_task = server_py_generator.acall_generate_code(question_html,server_instructions,solution)
        solution_html_task = question_solution_generator.acall_generate_code(query=question_html,solution_guide=solution)
        solution_html_flask_task = question_solution_generator_flask.acall_generate_code(question_html,solution_guide=solution)
        server_js, server_py, solution_html,solution_html_flask = await asyncio.gather(
            server_js_task,
            server_py_task,
            solution_html_task,
            solution_html_flask_task
        )
        logger.info("Successfully generated server JS, server PY, and solution HTML.")
        return server_js, server_py, solution_html,solution_html_flask
    except Exception as e:
        logger.error(f"Error during server and solution generation: {e}", exc_info=True)
        raise

async def generate_adaptive_module(question: str,
    metadata_dict: Optional[Dict[str, Any]] = None,
    instructions:Dict = {}):
    try:
        question_html = await generate_question_html(question,instructions)
        server_js, server_py, solution_html,solution_flask = await generate_server_and_solution(
            question_html, instructions=instructions
        )
        generated_content = {
            "question.html": question_html,
            "server.py": server_py,
            "server.js": server_js,
            "info.json": metadata_dict if metadata_dict else {},
            "solution.html": solution_html,
            "solution_flask.html":solution_flask
        }
        logger.debug(f"Generated Content: {generated_content}")
        return generated_content
    except Exception as e:
        logger.error(f"An error occurred in generate_adaptive_module: {e}", exc_info=True)
        raise

async def main():
    questions = [
        "Calculate the thermal efficiency of a heat engine with an input heat of 500 kJ and work output of 200 kJ."
        # "Determine the lift force on an aircraft wing if the lift coefficient is 0.4, the air density is 1.225 kg/m^3, the wing area is 25 m^2, and the velocity of the aircraft is 50 m/s.",
        # "Calculate the output voltage of a resistor-capacitor (RC) circuit with an input voltage of 10V, resistance of 1 kΩ, and capacitance of 100 µF after 5 seconds.",
        # "Determine the maximum tensile stress a steel rod can withstand if it has a diameter of 10 mm and a tensile force of 20 kN is applied.",
        # "Calculate the volume of material needed to 3D print a solid cylindrical part with a diameter of 50 mm and a height of 100 mm."
        # "I want to generate a question that will ask students to calculate the derivative of a function at most degree 4 but can have as low as 2 using the power rule and have random coefficients"
    ]

    total_tokens_used = 0

    # Run the module generation concurrently for all questions
    results= await asyncio.gather(*(generate_adaptive_module(question) for question in questions))

    # Process the results and sum the total tokens
    for result in results:
        logger.info(f"Generated content:\n{result}\n")

    logger.info(f"Total tokens used across all questions: {total_tokens_used}")
    return total_tokens_used

if __name__ == "__main__":
    asyncio.run(main())