import os
import json
import asyncio
from openai import AsyncOpenAI
from src.llm_generators.llm_templates import generate_metadata_template
from credentials import api_key
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Determine the base directory (two levels up from this file)
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct the full path to the tag.json file
cleaned_tags_file = os.path.join(base_dir, 'data', 'tag.json')

# Load Cleaned tags
def load_tags(filename=cleaned_tags_file):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data["cleaned_tags"]

client_async = AsyncOpenAI(api_key=api_key)
model = "gpt-3.5-turbo"

@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(1))
async def analyze_question(question, tags):
    prompt = generate_metadata_template.format(question=question, tags=tags)
    response = await client_async.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a professor at a University focused on mechanical engineering education. Please return the result in JSON format."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

async def generate_metadata_and_update(question):
    cleaned_tags = load_tags()
    metadata_response = await analyze_question(question, cleaned_tags)
    metadata = eval(metadata_response)
    return metadata

# # Example usage:
# async def main():
#     question = "What is 25x25?"
#     metadata = await generate_metadata_and_update(question)
#     print(metadata)

# # Run the main function
# asyncio.run(main())
