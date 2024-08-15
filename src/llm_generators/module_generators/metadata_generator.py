import json
import asyncio
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List
from ...credentials import api_key

MODEL = "gpt-4o-mini"
client_async = AsyncOpenAI(api_key=api_key)


class MetaData(BaseModel):
    uuid: str = Field(...,description="uuid: A universally unique identifier (UUID) for this item")
    title: str = Field(..., description="An appropriate title for the given question, return using CamelCase format")
    stem: str = Field(..., description="Additional context or a subtopic related to the main topic")
    topic: str = Field(..., description="The main topic or subject of the educational content")
    tags: List[str] = Field(..., description="An array of keywords or tags associated with the content")
    prereqs: List[str] = Field(..., description="An array of prerequisites needed to access or understand the content")
    isAdaptive: bool = Field(..., description="Designates whether the content necessitates any form of numerical computation. Assign as 'true' if the question involves any numerical computation; return 'false' if no computational effort is required")
class Response(BaseModel):
    question: str = Field(...,description="Original Question that was classified")
    metadata:MetaData

async def classify_question(question:str)->dict:
    prompt =  f"Generate metadat of the following question {question}"
    response = await client_async.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a professor at a University focused on mechanical engineering education. Please return the result in JSON format."},
            {"role": "user", "content": prompt}
        ], 
        response_format=Response,
    )
    cleaned_response = json.loads(response.choices[0].message.content)
    return cleaned_response
    
async def main():
    questions = [
    "A 5 kg object is moving at a speed of 10 m/s. Calculate the kinetic energy of the object.",
    "Solve the quadratic equation 3x^2 - 5x + 2 = 0 and find the roots.",
    "Explain the difference between a stack and a queue in data structures.",
    "Discuss the concept of electronegativity and its significance in chemical bonding."]
    results = await asyncio.gather(*(classify_question(question) for question in questions))
    return results
    
if __name__ == "__main__":
    results = asyncio.run(main())
    display = [print(f"\n Question : {result.get('question')} \n Classification: {result.get('metadata')} \n") for result in results]