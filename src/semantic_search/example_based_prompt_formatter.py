from dataclasses import dataclass,field
from typing import List, Dict
from .semantic_search import SemanticSearchManager
from .get_embeddings import GenerateEmbeddings
from .embedded_dataframe import EmbeddingDataFrame
from .llm_config import LLMConfig


@dataclass
class ExampleBasedPromptDataFrame:
    """
    A class designed to handle the configuration, validation, and generation of prompts based on examples 
    extracted from a DataFrame. This class integrates various components for embedding generation and semantic 
    search operations, allowing users to retrieve and format examples for use in language models.

    Attributes:
        example_input_column (str): The name of the column containing example inputs in the DataFrame.
        example_output_column (str): The name of the column containing the corresponding outputs for the examples.
        api_key (str): API key for accessing the language model.
        embedding_engine (str): The engine used for generating embeddings. Defaults to "text-embedding-ada-002".
        embedding_columns (str): The name of the column in the DataFrame that contains the embeddings. Defaults to "question_embedding".
        embedding_file (str): Path to the CSV file containing the DataFrame. Defaults to "src\data\Question_Embedding_20240128.csv".
        df_config (EmbeddingDataFrame): Configuration object for the DataFrame, initialized in `__post_init__`.
        llm_config (LLMConfig): Configuration for the language model, initialized in `__post_init__`.
        embedding_generator (GenerateEmbeddings): An instance for generating embeddings, initialized in `__post_init__`.
        semantic_search (SemanticSearchManager): Manages semantic search operations on the DataFrame, initialized in `__post_init__`.

    Methods:
        __post_init__():
            Post-initialization to set up the configurations after the main dataclass fields are initialized.

        extract_examples(query: str, threshold: float, num_examples: int) -> List[Dict]:
            Extracts examples from the DataFrame based on a semantic search query, threshold, and number of examples.

        format_examples(query: str, threshold: float, num_examples: int) -> str:
            Formats the extracted examples into a string, with each input and output pair presented.

        format_examples_prompt(template_text: str, query: str, threshold: float, num_examples: int) -> str:
            Creates a prompt by combining a template text with formatted examples based on the query and search criteria.
    """

    example_input_column: str
    example_output_column: str

    api_key: str
    embedding_engine: str = "text-embedding-ada-002"
    embedding_columns: str = "question_embedding"
    embedding_file: str = r"src\data\Question_Embedding_20240128.csv"

    df_config: EmbeddingDataFrame = field(init=False)
    llm_config: LLMConfig = field(init=False)
    embedding_generator: GenerateEmbeddings = field(init=False)
    semantic_search: SemanticSearchManager = field(init=False)

    def __post_init__(self):
        """
        Post-initialization to set up the configurations after the main dataclass fields are initialized.
        """
        # Initialize the DataFrame configuration
        self.df_config = EmbeddingDataFrame(
            csv_path=self.embedding_file,
            embedding_column=self.embedding_columns,
            example_input_column=self.example_input_column,
            expected_output_column=self.example_output_column
        )

        # Get the dataframe
        self.dataframe = self.df_config.validate_dataframe()
        
        # Initialize the LLM configuration
        self.llm_config = LLMConfig(
            api_key=self.api_key,
            model=self.embedding_engine,
            temperature=0
        )
        
        # Initialize the semantic search
        self.embedding_generator = GenerateEmbeddings(self.llm_config)
        self.semantic_search = SemanticSearchManager(self.df_config, self.embedding_generator)


    def extract_examples(self, query: str, threshold: float, num_examples: int) -> List[Dict]:
        """
        Extracts examples from the DataFrame based on a semantic search query, threshold, and number of examples.

        Args:
            query (str): The query text for which to search similar examples.
            threshold (float): The similarity threshold to filter results.
            num_examples (int): The number of examples to return.

        Returns:
            List[Dict]: A list of dictionaries, each containing an 'input' and 'output' key with corresponding example values.
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

        Args:
            query (str): The query text for which to search similar examples.
            threshold (float): The similarity threshold to filter results.
            num_examples (int): The number of examples to return.

        Returns:
            str: A formatted string of examples, where each input and output pair is separated by a newline.
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
    search_column = "question"
    output_column = "question.html"
    from ..credentials import api_key

    formatter = ExampleBasedPromptDataFrame(
        example_input_column=search_column, 
        example_output_column=output_column, 
        api_key=api_key
    )

    questions = [
        "What is the role of mitochondria in cellular respiration and how does it contribute to energy production in eukaryotic cells?",
        "Explain the concept of entropy in thermodynamics and how it relates to the second law of thermodynamics.",
        "How does the principle of superposition apply to the analysis of electrical circuits in the context of Ohm's Law?",
        "What are the key differences between classical mechanics and quantum mechanics in the behavior of particles at the microscopic scale?"
    ]

    prompts = [
        "This is the prompt for mitochondria:",
        "This is the prompt for entropy:",
        "This is the prompt for superposition principle:",
        "This is the prompt for classical vs quantum mechanics:"
    ]

    for i, question in enumerate(questions):
        examples = formatter.format_examples_prompt(
            template_text=prompts[i], 
            query=question, 
            threshold=0.5, 
            num_examples=1
        )
        print(f"Prompt for Question {i+1}:\n{examples}\n{'='*50}\n")

    formatter.pretty_print_extracted_examples(questions[0],0.5,3)

if __name__ == "__main__":
    main()



    