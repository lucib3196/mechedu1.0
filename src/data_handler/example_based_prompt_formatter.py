import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Dict

from .semantic_search import SemanticSearchManager
from .generate_embeddings import GenerateEmbeddings
from .embedded_dataframe import EmbeddingDataFrame
from ..llm_module_generator.llm_base import LLMConfig

# Determine the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))



@dataclass
class ExampleBasedPromptDataFrame:
    example_input_column: str
    example_output_column: str

    api_key: str
    embedding_engine: str = "text-embedding-3-small"
    embedding_columns: str = "embeddings-3-small"
    embedding_file: str = os.path.join(base_dir, '..', 'data', 'question_embeddings_2024_9_11.csv')


    df_config: EmbeddingDataFrame = field(init=False)
    is_adaptive: bool = True
    llm_config: LLMConfig = field(init=False)
    embedding_generator: GenerateEmbeddings = field(init=False)
    semantic_search: SemanticSearchManager = field(init=False)
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self):
        if not self._initialized:
            print("Initializing ExampleBasedPromptDataFrame...")
            if self.is_adaptive:
                self.df_config = EmbeddingDataFrame(
                    csv_path=self.embedding_file,
                    embedding_column=self.embedding_columns,
                    example_input_column=self.example_input_column,
                    expected_output_column=self.example_output_column,
                )
            else:
                self.df_config = EmbeddingDataFrame(
                    csv_path=self.embedding_file,
                    embedding_column=self.embedding_columns,
                    example_input_column=self.example_input_column,
                    expected_output_column=self.example_output_column,
                    filter_condition=("isAdaptive",True)
                )
            self.dataframe = self.df_config.validate_dataframe()

            self.llm_config = LLMConfig(
                api_key=self.api_key,
                model=self.embedding_engine,
                temperature=0
            )
            self.embedding_generator = GenerateEmbeddings(self.llm_config)
            self.semantic_search = SemanticSearchManager(self.df_config, self.embedding_generator)
            self._initialized = True
            print("Initialization complete.")
        else:
            print("ExampleBasedPromptDataFrame already initialized.")

    @classmethod
    def get_instance(cls, example_input_column, example_output_column, api_key):
        global _example_based_prompt_dataframe_instance
        if _example_based_prompt_dataframe_instance is None:
            _example_based_prompt_dataframe_instance = cls(
                example_input_column=example_input_column, 
                example_output_column=example_output_column, 
                api_key=api_key
            )
        return _example_based_prompt_dataframe_instance

    def extract_examples(self, query: str, threshold: float, num_examples: int) -> List[Dict]:
        """
        Extracts examples from the DataFrame based on a semantic search query, threshold, and number of examples.
        """
        filtered_results = self.semantic_search.filtered_similarities(query, threshold, num_examples)
        all_examples = []
        for result in filtered_results:
            if isinstance(result, tuple) and len(result) == 3:
                index, input_example, _ = result
                example = {
                    "input": input_example,
                    "output": self.dataframe.loc[index, self.example_output_column]
                }
                all_examples.append(example)
        return all_examples

    def format_examples(self, query: str, threshold: float, num_examples: int) -> str:
        """
        Formats the extracted examples into a string, with each input and output pair presented.
        """
        examples = self.extract_examples(query, threshold, num_examples)
        formatted_example = ""
        for example in examples:
            formatted_example += f"input:{example['input']}\noutput:{example['output']}\n"
        return formatted_example
    
    def format_examples_prompt(self, template_text: str, query: str, threshold: float, num_examples: int) -> str:
        """
        Creates a prompt by combining a template text with formatted examples based on the query and search criteria.

        Args:
            template_text (str): The base text template to which the examples will be appended.
            query (str): The query text for which to search similar examples.
            threshold (float): The similarity threshold to filter results.
            num_examples (int): The number of examples to return.

        Returns:
            str: A full prompt with the template text followed by the formatted examples.
        """
        prompt = f"{template_text}\n{self.format_examples(query, threshold, num_examples)}"
        return prompt
    
    def pretty_print_extracted_examples(self, query: str, threshold: float, num_examples: int):
        """
        Prints the extracted examples in a formatted table.

        Args:
            query (str): The input query text for which to extract examples.
            threshold (float): The similarity threshold to filter results.
            num_examples (int): The number of examples to return.

        Returns:
            None
        """
        print(f"Extracted Examples for: '{query}'\n")
        print(f"{'Input Example':<60}{'Output Example':<60}")
        print("-" * 120)
        
        extracted_examples = self.extract_examples(query, threshold, num_examples)
        
        for example in extracted_examples:
            # Truncate long strings for display
            display_input = (example['input'][:57] + '...') if len(example['input']) > 60 else example['input']
            display_output = (example['output'][:57] + '...') if len(example['output']) > 60 else example['output']
            print(f"{display_input:<60}{display_output:<60}")
        
        print("\n")


def main():
    # Define column names
    search_column = "question"
    output_column = "question.html"

    # Import API key
    from ..credentials import api_key

    # Initialize the formatter with the provided API key and column names
    formatter = ExampleBasedPromptDataFrame(
        example_input_column=search_column, 
        example_output_column=output_column, 
        api_key=api_key
    )

    # List of questions to be processed
    questions = [
        "What is the role of mitochondria in cellular respiration and how does it contribute to energy production in eukaryotic cells?",
        "Explain the concept of entropy in thermodynamics and how it relates to the second law of thermodynamics.",
        "How does the principle of superposition apply to the analysis of electrical circuits in the context of Ohm's Law?",
        "What are the key differences between classical mechanics and quantum mechanics in the behavior of particles at the microscopic scale?"
    ]

    # Corresponding prompts for each question
    prompts = [
        "This is the prompt for mitochondria:",
        "This is the prompt for entropy:",
        "This is the prompt for superposition principle:",
        "This is the prompt for classical vs quantum mechanics:"
    ]

    # Generate and print formatted examples for each question
    for i, question in enumerate(questions):
        examples = formatter.format_examples_prompt(
            template_text=prompts[i], 
            query=question, 
            threshold=0.5, 
            num_examples=1,
        )
        print(f"\nPrompt for Question {i + 1}:\n{examples}\n{'='*50}\n")

    # Pretty print extracted examples for the first question
    formatter.pretty_print_extracted_examples(questions[0], threshold=0.5, num_examples=3)

if __name__ == "__main__":
    main()

    