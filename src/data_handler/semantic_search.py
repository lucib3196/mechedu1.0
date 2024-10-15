from dataclasses import dataclass
from openai import OpenAI
import numpy as np
from typing import List,Tuple
import os

from .generate_embeddings import GenerateEmbeddings
from .embedded_dataframe import EmbeddingDataFrame



def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@dataclass
class SemanticSearchManager:
    """
    A class to manage the configuration, validation, and processing of a DataFrame for semantic search operations.

    This class handles validating the DataFrame, generating embeddings for input queries, 
    and calculating similarity scores between the query embeddings and the embeddings stored in the DataFrame.

    Attributes:
        embedded_dataframe_config (EmbeddingDataFrame): Configuration object containing the DataFrame 
            and information about the relevant columns used in the semantic search.
        embedding_generator (GenerateEmbeddings): An instance responsible for generating embeddings 
            using a language model.
    
    Methods:
        get_similarities_dataframe(query: str) -> List[Tuple[int, str, float]]:
            Validates the DataFrame and computes similarity scores between the query embedding 
            and the embeddings in the DataFrame.

        filtered_similarities(query: str, threshold: float, n_examples: int) -> List[Tuple[int, str, float]]:
            Filters and returns the top N similarities that exceed a specified threshold.
    """
    embedded_dataframe_config: EmbeddingDataFrame
    embedding_generator: GenerateEmbeddings

    def get_similarities_dataframe(self, query: str) -> List[Tuple[int, str, float]]:
        """
        Validates the DataFrame and computes similarity scores between the query embedding 
        and the embeddings in the DataFrame.

        Args:
            query (str): The input text for which to compute similarity scores.

        Returns:
            List[Tuple[int, str, float]]: A list of tuples, each containing the row index, 
            the example input from the DataFrame, and the similarity score between the query and the example.
        """
        df = self.embedded_dataframe_config.validate_dataframe()
        embeddings = self.embedding_generator.get_embeddings_sync(query=query)
        return [
            (
                index, 
                row[self.embedded_dataframe_config.example_input_column], 
                cosine_similarity(row[self.embedded_dataframe_config.embedding_column],embeddings)
            )
            for index, row in df.iterrows()
            if self.embedded_dataframe_config.embedding_column in row and isinstance(row[self.embedded_dataframe_config.embedding_column], list)
        ]

    def filtered_similarities(self, query: str, threshold: float, n_examples: int) -> List[Tuple[int, str, float]]:
        """
        Filters and returns the top N similarities that exceed a specified threshold.

        Args:
            query (str): The input text for which to compute similarity scores.
            threshold (float): A similarity threshold; only results with a score equal to or greater than 
                this value will be included.
            n_examples (int): The number of top results to return.

        Returns:
            List[Tuple[int, str, float]]: A list of the top N tuples, each containing the row index, 
            the example input from the DataFrame, and the similarity score, sorted by similarity in descending order.
        """
        semantic_search_results = self.get_similarities_dataframe(query)
        filtered_results = [result for result in semantic_search_results if result[2] >= threshold]
        return sorted(filtered_results, key=lambda x: x[2], reverse=True)[:n_examples]
    
    def pretty_print_filtered_result(self, query: str, threshold: float, n_examples: int) -> None:
        """
        Prints the filtered semantic search results in a formatted table.

        Args:
            query (str): The input text for which to perform the semantic search.
            threshold (float): A similarity threshold; only results with a score equal to or greater than this value will be included.
            n_examples (int): The number of top results to display.

        Returns:
            None
        """
        results = self.filtered_similarities(query, threshold, n_examples)
        
        print(f"\nSemantic Search Results for: '{query}'\n")
        print(f"{'Index':<10}{'Similarity Score':<20}{'Semantic Example':<60}")
        print("-" * 90)
        
        for index, example, similarity_score in results:
            display_example = (example[:57] + '...') if len(example) > 60 else example
            print(f"{index:<10}{similarity_score:<20.4f}{display_example:<60}")
        
        if not results:
            print("No results found that meet the threshold.\n")
        else:
            print("\nDisplayed top results based on the given threshold and number of examples.\n")


def main():
    # Set up file paths and column names
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'Question_Embedding_20240128.csv')
    embedding_column = "question_embedding"
    search_column = "question"
    output_column = "question.html"
    
    # Initialize the DataFrame configuration
    df_config = EmbeddingDataFrame(csv_path, embedding_column, search_column, output_column)
    
    # Initialize the LLM configuration
    llm_config = LLMConfig(
        api_key=api_key,
        model="text-embedding-ada-002",
        temperature=0
    )
    
    # Set up the embedding generator
    embedding_generator = GenerateEmbeddings(llm_config)

    # List of questions to be processed
    questions = [
        "What is the role of mitochondria in cellular respiration and how does it contribute to energy production in eukaryotic cells?",
        "Explain the concept of entropy in thermodynamics and how it relates to the second law of thermodynamics.",
        "How does the principle of superposition apply to the analysis of electrical circuits in the context of Ohm's Law?",
        "What are the key differences between classical mechanics and quantum mechanics in the behavior of particles at the microscopic scale?"
    ]

    # Initialize the semantic search manager
    semantic_search = SemanticSearchManager(df_config, embedding_generator)

    # Perform semantic search and print results
    for question in questions:
        semantic_search.pretty_print_filtered_result(question, threshold=0.7, top_n=3)

if __name__ == "__main__":
    main()
