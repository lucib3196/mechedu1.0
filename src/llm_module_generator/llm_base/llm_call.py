import asyncio
import json
from dataclasses import dataclass, field
from typing import Union, Dict
import re

from openai import AsyncOpenAI
import openai
from pydantic import BaseModel

from...logging_config.logging_config import get_logger
from ...credentials import api_key
from .llm_config import LLMConfig
logger = get_logger(__name__)

def extract_json(response:str):
    pattern = r'\{[^}]*\}'
    match = re.search(pattern, response)
    if match:
        json_string = match.group(0) 
        return json_string.strip()
    else:
        return None
@dataclass
class LLM_Call():
    llm_config: LLMConfig
    total_tokens: int = field(default=0,init=False)
    
    def __post_init__(self):
        self.client_async = AsyncOpenAI(api_key = self.llm_config.api_key)
        
    async def acall(self, prompt: str, response_format: Union[Dict, BaseModel] = None): # type: ignore
        try:
            response_format = response_format if response_format is not None else {"type": "json_object" }
            print(response_format)
            response = await self.client_async.beta.chat.completions.parse( # type: ignore
                model = self.llm_config.model,
            messages=[
                {"role": "system", "content": "You are a helpul assistant. Please return the result in JSON format."},
                {"role": "user", "content": prompt}
            ],
            response_format=response_format if response_format is not None else {"type": "json_object" },
            )
            
            completion = response.choices[0].message.content
            try: 
                completion = json.loads(completion)
            except (json.JSONDecodeError, ValueError):
                completion = json.loads(extract_json(completion)) 
            self.total_tokens += response.usage.total_tokens
            return completion
        except ValueError as e:
            logger.exception("Error Could not complete LLM Call")
    
    def get_total_tokens(self)->int:
        return self.total_tokens
        
def main():
    llm_config = LLMConfig(api_key=api_key, model="chatgpt-4o-latest", temperature=0)
    completion_model = LLM_Call(llm_config)
    
    print(asyncio.run(completion_model.acall("Hello")))
    print(asyncio.run(completion_model.acall("How are you")))
    print(completion_model.get_total_tokens())

if __name__ == "__main__":
    main()