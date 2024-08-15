from typing import List, Dict
from dataclasses import dataclass
import pandas as pd

from ..data_handler import validate_and_process_csv
from ..data_handler.utils import is_valid_columns

from dataclasses import dataclass

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

    def validate_dataframe(self)->pd.DataFrame:
        """Validates the DataFrame to ensure it contains the necessary columns for embedding search.

        This method loads the DataFrame from the specified CSV path, checks that the 
        required columns (`example_input_column` and `expected_output_column`) are present 
        and valid, and ensures there are no missing values in the expected output column.

        Returns:
            pandas.DataFrame: The validated DataFrame if successful.
            str: An error message if the validation fails.
        """
        # Load in dataframe
        self.dataframe = validate_and_process_csv(self.csv_path, self.embedding_column)
        # Check and ensure dataframe is ready for embeddings
        columns = [self.example_input_column, self.expected_output_column]
        if is_valid_columns(self.dataframe, columns):
            self.dataframe = self.dataframe.dropna(subset=[self.expected_output_column])
            return self.dataframe
        else:
            return "DataFrame is invalid"


def main():
    file_path = r"src\data\Question_Embedding_20240128.csv"
    embedding_column = r"question_embedding"
    search_column = "question.html"
    output_column = "server.py"

    df = EmbeddingDataFrame(file_path, embedding_column,search_column,output_column).validate_dataframe()
    print(df.head())


if __name__ == "__main__":
    main()