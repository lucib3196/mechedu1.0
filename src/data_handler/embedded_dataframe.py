from typing import List, Dict, Optional, Tuple,Any
from dataclasses import dataclass
import pandas as pd
from dataclasses import dataclass,field
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
        filter_condition (Optional[Tuple[str, Any]]): A tuple containing the column name and value to filter out unwanted rows.
    """
    csv_path: str
    embedding_column: str
    example_input_column: str
    expected_output_column: str
    filter_condition: Optional[Tuple[str, Any]] = None

    dataframe: pd.DataFrame = field(init=False, default=None)


    def validate_dataframe(self) -> Optional[pd.DataFrame]:
        """Validates the DataFrame to ensure it contains the necessary columns for embedding search.

        This method loads the DataFrame from the specified CSV path, checks that the 
        required columns (`example_input_column` and `expected_output_column`) are present 
        and valid, and ensures there are no missing values in the expected output column.

        Returns:
            pandas.DataFrame: The validated DataFrame if successful.
            None: If validation fails, returns None.
        """
        try:
            # Load the dataframe
            self.dataframe = validate_and_process_csv(self.csv_path, self.embedding_column)
            logger.debug(f"DataFrame loaded with columns: {self.dataframe.columns.tolist()}")

            # Apply filtering if a filter condition is provided
            if self.filter_condition:
                column_name, filter_value = self.filter_condition
                if column_name in self.dataframe.columns:
                    logger.info(f"Filtering out rows where {column_name} == {filter_value}")
                    self.dataframe = self.dataframe[self.dataframe[column_name] != filter_value]
                else:
                    logger.error(f"Filter column '{column_name}' not found in the DataFrame.")
                    return self.dataframe

            # Validate required columns
            required_columns = [self.example_input_column, self.expected_output_column]
            if is_valid_columns(self.dataframe, required_columns):
                self.dataframe = self.dataframe.dropna(subset=[self.expected_output_column])
                logger.info("DataFrame validated successfully.")
                return self.dataframe
            else:
                logger.error("Required columns are missing or invalid.")
                return None

        except ValueError as e:
            logger.exception(f"DataFrame validation and processing failed: {e}")
            return None

    def drop_unwanted(self):
        """Optional method to print or handle the unwanted column condition."""
        if self.filter_condition:
            logger.info(f"Filter condition: {self.filter_condition}")
        else:
            logger.info("No filter condition provided.")



def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'Question_embedding_20240902.csv')
    
    logger.debug(f"Base directory set to: {base_dir}")
    logger.debug(f"CSV path for question embeddings constructed: {csv_path}")
    try:
        manager = EmbeddingDataFrame(csv_path,"question_embedding", "question", "question.html", filter_condition=("isAdaptive",True))
        df = manager.validate_dataframe()
        print(df["isAdaptive"])
        print(df.head())
        print(len(df))
    except ValueError as e:
        logger.error(f"Failed to Create embedded dataframe error {e}")
if __name__ == "__main__":
    main()
