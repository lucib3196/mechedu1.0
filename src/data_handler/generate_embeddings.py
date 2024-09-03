from dataclasses import dataclass
from typing import Optional, List

from openai import OpenAI
from ..credentials import api_key
from ..llm_module_generator.llm_base import LLMConfig


@dataclass
class GenerateEmbeddings:
    """
    A class to generate and display embeddings for given text queries using a specified language model.

    Attributes:
        llm_config (LLMConfig): Configuration object for the language model, including API key and model name.
    
    Methods:
        get_embeddings_sync(query: str) -> List[float]:
            Generates embeddings for a given text query using the specified language model.
        
        pretty_print_embeddings(queries: List[str], length_embeddings: int = 10) -> None:
            Generates and prints embeddings for a list of text queries, showing only the first few values 
            based on the specified length.
    """
    llm_config: LLMConfig
    
    def get_embeddings_sync(self, query: str)->List[float]:
        """
        Generates embeddings for a given text query using the specified language model.

        Args:
            query (str): The input text for which to generate embeddings.

        Returns:
            List[float]: A list of floating-point numbers representing the embedding of the input text.
        """
        client = OpenAI(api_key=self.llm_config.api_key)
        response = client.embeddings.create(input=query, model=self.llm_config.model)
        embeddings = response.data[0].embedding
        return embeddings

    def pretty_print_embeddings(self, queries: List[str], length_embeddings: int = 10)->None:
        """
        Generates and prints embeddings for a list of text queries, displaying only the first few values.

        Args:
            queries (List[str]): A list of text queries for which to generate and display embeddings.
            length_embeddings (int): The number of embedding values to display for each query. Defaults to 10.

        Returns:
            None
        """
        results = [self.get_embeddings_sync(query=query) for query in queries]
        for i, result in enumerate(results):
            print(f"\n Original Input: {queries[i]}")
            print(f"Embeddings: {result[:length_embeddings]}")  # Slice to print only a portion of the embeddings
            print('*' * 50)



def main():
    queries = [
        "What is a car?",
        "What is the capital of France?",
        "This is just some text"
    ]
    
    # Initialize the LLM configuration
    llm_config = LLMConfig(
        api_key=api_key,
        model="text-embedding-ada-002",
        temperature=0
    )
    
    # Generate embeddings based on the LLM configuration
    generate_embeddings = GenerateEmbeddings(llm_config)
    
    # Pretty print the embeddings for the given queries
    generate_embeddings.pretty_print_embeddings(queries)

if __name__ == "__main__":
    main()
