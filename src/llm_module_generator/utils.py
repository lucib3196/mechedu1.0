import re
from src.llm_module_generator.physics_module_generator.math_js_retriever import llm
from .llm_base import LLM_Call, LLMConfig
from src.credentials import api_key
from typing import Optional
from pydantic import BaseModel, Field
import asyncio
import json

class Response(BaseModel):
    question:str = Field(...,description ="The full question that will converted into a online assesment")
    additional_instructions: Optional[str] = Field(...,description="The cleaned up additional instructions")
async def analyze_input_query(query:str):
    llm = LLM_Call(LLMConfig(api_key, "gpt-4o-mini",0))
    prompt = f"""You are tasked with analyzing and refining a given query, which will be used to generate complete, answerable questions for an online educational assessment for students. The goal of this analysis is to convert the input into questions that can be part of an online module, ensuring the questions are relevant, usable, and clearly defined for students. The process of refining and extracting the question and instructions should help define the scope of the module, making sure it aligns with the learning objectives.

    The query may come in different forms:

    A clear, complete question.
    A question with additional instructions (guiding how the assessment should be shaped).
    Vague instructions or an incomplete question.
    Your task is to process the query and determine the appropriate response based on the following criteria:

    Complete Questions: If the input is a fully-formed, answerable question that requires no changes, simply return the question unchanged.

    Questions with Additional Instructions: If the input contains a question with additional instructions (e.g., considerations or requirements for generating the online assessment), clean up and clarify the instructions, making sure they are precise and aligned with the learning goals. Expand on them if needed, and ensure that the final output is a complete, answerable question that incorporates the user’s considerations.

    Vague Instructions Without a Clear Question: If the input only contains vague or incomplete instructions without a clear question, use the provided information to generate a well-formed, answerable question that can be part of the educational module.

    Examples to guide your output:

    Example 1:

    Input: "A ball is traveling along a straight path for a total distance of 50 meters in 30 seconds. Calculate its velocity."
    Response: Return the input question unchanged.
    Example 2:

    Input: "A ball is traveling along a straight path for a total distance of 50 meters in 30 seconds. Calculate its velocity. I want to ensure that the question is dynamic and includes additional units such as USCS (feet)."
    Response:
    Clean up the instructions: "Ensure the question is dynamic and provides velocity calculation in both meters and USCS units (feet)."
    Final question: "A ball is traveling along a straight path for a total distance of 50 meters in 30 seconds. Calculate its velocity in both meters per second and feet per second."
    Example 3:

    Input: "Generate a projectile motion question."
    Response: Generate a complete question: "A ball is launched at an angle of 45 degrees with an initial velocity of 20 m/s. Calculate the maximum height and the total time it stays in the air."
    Additional Considerations:

    Ensure that the returned question is fully answerable, relevant for student assessments, and suitable for the learning module.
    Instructions should be cleaned up to ensure clarity and relevance, aligning with the educational goals.
    For vague instructions, generate a well-formed question that covers the required topic comprehensively.



    user query: {query}
    """
    response = await llm.acall(prompt,response_format =Response )
    question = response.get("question")
    additional_instructions = response.get("additional_instructions")

    return f"Question:{question}\nAdditional_instructions{additional_instructions}"
    

async def main():
    queries = [
    "I want to generate a question about derivatives that ask students to solve the derivative of a function using the power rule, it should be up to degree 4 and should have random coeffiencients. ",
    "Explain the process of mitosis. Make sure it includes diagrams and breaks down the phases for high school students.",
    "Generate a question about Ohm's Law.",
    "Who is the author of the novel '1984'?",
    "Solve the quadratic equation x^2 - 4x + 4 = 0. Also, provide real-life applications of quadratic equations.",
    "A projectile is fired at an angle of 30 degrees with an initial velocity of 50 m/s. Calculate its range and time of flight. Make sure to include both SI units and USCS units in the answer.",
    "Create a question about the digestive system.",
    "Describe the process of evaporation. Include examples from everyday life, such as water boiling or puddles drying.",
    "Generate a physics question related to momentum and collisions.",
    "What are the three branches of government in the United States?"]


    results = await asyncio.gather(*[analyze_input_query(query) for query in queries])
    for result in results:
        print(result)

if __name__ == "__main__":
    asyncio.run(main())