from dataclasses import dataclass

@dataclass
class LLMConfig:
    api_key:str
    model:str
    temperature:float
