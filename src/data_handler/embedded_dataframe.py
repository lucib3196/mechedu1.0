from typing import List, Dict
from dataclasses import dataclass
import pandas as pd
from dataclasses import dataclass
import os

from .validate_process_csv import validate_and_process_csv
from .utils import is_valid_columns
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class EmbeddingDataFrame:
    """
    Processes and validates a DataFrame for embedding-based searches.

    This class is designed to load a CSV file, validate the structure of the DataFrame, 
    and ensure that the specified columns for embedding, input examples, and corresponding 
    outputs are valid. The `validate_dataframe` method checks for the presence of the 
    required columns and handles missing data in the output column.

    Attributes:
        csv_path (str): Path to the CSV file to be processed.
        embedding_column (str): The name of the column containing the embeddings.
        example_input_column (str): The name of the column representing the input examples for search.
        expected_output_column (str): The name of the column representing the expected output corresponding to the input examples.
    """
    csv_path: str
    embedding_column: str
    example_input_column: str
    expected_output_column: str

    def __post_init__(self):
        self.logger = get_logger(__name__)

    def validate_dataframe(self)->pd.DataFrame:
        """Validates the DataFrame to ensure it contains the necessary columns for embedding search.

        This method loads the DataFrame from the specified CSV path, checks that the 
        required columns (`example_input_column` and `expected_output_column`) are present 
        and valid, and ensures there are no missing values in the expected output column.

        Returns:
            pandas.DataFrame: The validated DataFrame if successful.
            str: An error message if the validation fails.
        """
        try:
            # Load in dataframe
            self.dataframe = validate_and_process_csv(self.csv_path, self.embedding_column)
            # Check and ensure dataframe is ready for embeddings
            columns = [self.example_input_column, self.expected_output_column]
            if is_valid_columns(self.dataframe, columns):
                self.dataframe = self.dataframe.dropna(subset=[self.expected_output_column])
                self.logger.info("Embedded DataFrame Loaded Succesfully")
                return self.dataframe
        except ValueError as e:
            self.logger.exception(f"DataFrame validation and processing failed: {e}")
            return None


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'Question_Embedding_20240128.csv')
    
    logger.debug(f"Base directory set to: {base_dir}")
    logger.debug(f"CSV path for question embeddings constructed: {csv_path}")
    try:
        df = EmbeddingDataFrame(csv_path,"question_embedding", "question", "question.html")
    except ValueError as e:
        logger.error(f"Failed to Create embedded dataframe error {e}")
if __name__ == "__main__":
    main()