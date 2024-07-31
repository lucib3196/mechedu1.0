from dataclasses import dataclass, field
import pandas as pd

@dataclass
class LLMConfig:
    csv_path: str
    embedding_column: str
    embedding_engine: str
    search_column: str
    output_column: str
    n_examples: int
    similarity_threshold: float
    llm_model: str
    temperature: float
    embedding_model: str
    dataframe: pd.DataFrame = field(init=False, default=None)

# # Example instantiation
# config = LLMConfig(
#     csv_path="path/to/csv",
#     embedding_column="embedding",
#     embedding_engine="engine",
#     search_column="search",
#     output_column="output",
#     n_examples=5,
#     similarity_threshold=0.8,
#     llm_model="model_name",
#     temperature=0.5,
#     embedding_model="embedding_model_name"
# )
# print(config)
