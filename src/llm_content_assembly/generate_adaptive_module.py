from ..llm_module_generator.physics_module_generator.module_generator import question_html_generator, question_solution_generator, server_js_generator, server_py_generator
import asyncio
from ..llm_module_generator.physics_module_generator.llm_templates import server_template_code_guide, solution_improvement_prompt
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)

async def generate_adaptive_module(question: str,metadata_dict:dict = None, solution_guide: str = None):
    question_html = await question_html_generator.acall_generate_code(question)
    additional_instructions = f"{server_template_code_guide} \n {solution_guide}" if solution_guide else None
    logger.info(f"\nThis is the solution guide: {solution_guide if solution_guide else 'No solution guide provided'}\n")

    try:
        server_js, server_py, solution_html = await asyncio.gather(
            server_js_generator.acall_generate_code(question_html, additional_instructions=additional_instructions),
            server_py_generator.acall_generate_code(question_html, additional_instructions=additional_instructions),
            question_solution_generator.acall_generate_code(question_html, additional_instructions=additional_instructions)
        )
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise

    # Get and log total tokens used
    question_html_tokens = question_html_generator.get_total_tokens()
    server_js_tokens = server_js_generator.get_total_tokens()
    server_py_tokens = server_py_generator.get_total_tokens()
    solution_html_tokens = question_solution_generator.get_total_tokens()

    total_tokens = question_html_tokens + server_js_tokens + server_py_tokens + solution_html_tokens
    logger.info(f"Tokens used for question '{question}': {total_tokens}")
    
    generated_content = {
        "question.html": question_html,
        "server.py": server_py,
        "server.js": server_js,
        "info.json": metadata_dict,
        "solution.html": solution_html,
    }
    return generated_content, total_tokens


async def main():
    questions = [
        "Calculate the thermal efficiency of a heat engine with an input heat of 500 kJ and work output of 200 kJ.",
        "Determine the lift force on an aircraft wing if the lift coefficient is 0.4, the air density is 1.225 kg/m^3, the wing area is 25 m^2, and the velocity of the aircraft is 50 m/s.",
        "Calculate the output voltage of a resistor-capacitor (RC) circuit with an input voltage of 10V, resistance of 1 kΩ, and capacitance of 100 µF after 5 seconds.",
        "Determine the maximum tensile stress a steel rod can withstand if it has a diameter of 10 mm and a tensile force of 20 kN is applied.",
        "Calculate the volume of material needed to 3D print a solid cylindrical part with a diameter of 50 mm and a height of 100 mm."
    ]

    total_tokens_used = 0

    # Run the module generation concurrently for all questions
    results = await asyncio.gather(*(generate_adaptive_module(question) for question in questions))

    # Process the results and sum the total tokens
    for result in results:
        total_tokens_used += result["total_tokens"]
        logger.info(f"Generated content:\n{result}\n")

    logger.info(f"Total tokens used across all questions: {total_tokens_used}")
    return total_tokens_used

if __name__ == "__main__":
    asyncio.run(main())
