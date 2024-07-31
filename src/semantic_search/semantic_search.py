from src.data_processing.csv_processing import validate_and_process_csv
from credentials import api_key
from openai import OpenAI
import pandas as pd
from dataclasses import dataclass,field
import numpy as np
from src.llm_generators.LLMConfig import LLMConfig
from typing import List, Dict
import os
def isvalid_column(df:pd.DataFrame, column:str)->pd.DataFrame:
    return (column in df.columns)

@dataclass
class SemanticSearch(LLMConfig):
    
    def get_dataframe(self) -> pd.DataFrame:
        try:
            self.dataframe = validate_and_process_csv(self.csv_path, self.embedding_column)
            # Exclude rows with missing values for the output_column
            valid_rows = self.dataframe.dropna(subset=[self.output_column])
            self.dataframe = valid_rows
            return self.dataframe
        except ValueError as e:
            print(e)
            return None
    
    def validate_columns(self) -> bool:
        if self.dataframe is None:
            self.get_dataframe()
        valid_columns = [self.search_column, self.output_column, self.embedding_column]
        invalid_columns = [column for column in valid_columns if not isvalid_column(self.dataframe, column)]
        if invalid_columns:
            print(f"One or more columns are not valid: {', '.join(invalid_columns)}")
            return False
        return True

    def semantic_search(self, query: str) -> List[tuple]:
        if self.validate_columns():
            try:
                # Define OpenAI Client 
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.embeddings.create(input=query, model=self.embedding_engine)
                embeddings = response.data[0].embedding
                similarities = [
                    (index, row[self.search_column], np.dot(row[self.embedding_column], embeddings))
                    for index, row in self.dataframe.iterrows()
                    if self.embedding_column in row and isinstance(row[self.embedding_column], list)
                ]
                filtered_similarities = [entry for entry in similarities if entry[2] >= self.similarity_threshold]
                sorted_matches = sorted(filtered_similarities, key=lambda x: x[2], reverse=True)[:self.n_examples]
                return sorted_matches
            except Exception as e:
                print(f"An error occurred: {e}")
                return []

    def extract_examples(self, query: str) -> List[Dict[str, str]]:
        semantic_results = self.semantic_search(query)
        all_examples = []
        for result in semantic_results:
            if isinstance(result, tuple) and len(result) == 3:
                index, input_answer, _ = result
                example = {
                    "input": input_answer,
                    "output": self.dataframe.loc[index, self.output_column]
                }
                all_examples.append(example)
            else:
                print(f"Unexpected format for 'result': {result}")
        return all_examples

    def pretty_print_semantic_results(self, query: str):
        semantic_results = self.semantic_search(query)
        print(f"Semantic Search Results for: '{query}'\n")
        print(f"{'Index':<10}{'Similarity Score':<20}{'Semantic Example':<60}")
        print("-" * 90)
        for index, example, similarity_score in semantic_results:
            display_example = (example[:100] + '...') if len(example) > 60 else example
            print(f"{index:<10}{similarity_score:<20.2f}{display_example:<60}")
        print("\n")

    def pretty_print_extracted_examples(self, query: str):
        print(f"Extracted Examples for: '{query}'\n")
        print(f"{'Input Example':<60}{'Output Example':<60}")
        print("-" * 120)
        
        extracted_examples = self.extract_examples(query)
        for example in extracted_examples:
            # Truncate long strings for display
            display_input = (example['input'][:57] + '...') if len(example['input']) > 60 else example['input']
            display_output = (example['output'][:57] + '...') if len(example['output']) > 60 else example['output']
            print(f"{display_input:<60}{display_output:<60}")
        print("\n")
        

# # Example Usage
# csv_path = r"src\data\Question_Embedding_20240128.csv"
# semantic_search = SemanticSearch(
#     csv_path=csv_path,
#     embedding_column="question_embedding",
#     embedding_engine="text-embedding-ada-002",
#     search_column="question",
#     output_column="question.html",
#     similarity_threshold=0.5,
#     n_examples=3
# )
