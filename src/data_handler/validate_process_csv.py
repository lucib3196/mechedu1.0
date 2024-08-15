import pandas as pd
from .utils import load_df
from .process_embeddings import process_embeddings

def validate_and_process_csv(csv_path: str, embedding_column: str) -> pd.DataFrame:
    """
    Validates the CSV file and processes the embedding column.

    Parameters:
    - csv_path (str): The path to the CSV file.
    - embedding_column (str): The name of the column containing embeddings.

    Returns:
    - pd.DataFrame: The processed DataFrame with embeddings.

    Raises:
    - ValueError: If the CSV file is invalid or processing fails.
    """
    try:
        df = load_df(csv_path)
        if df is not None:
            return process_embeddings(df, embedding_column)
        else:
            raise ValueError(f"Failed to load CSV from {csv_path}")
    except Exception as e:
        raise ValueError(f"Failed to process CSV at {csv_path}: {e}") from e
    
    
if __name__ == "__main__":
    file_path = r"mechedu1.0\src\data\Question_Embedding_20240128.csv"
    embedding_column = r"question_embedding"
    df = validate_and_process_csv(csv_path = file_path, embedding_column=embedding_column)
    print(df.head())