import os
import pandas as pd

from ..logging_config.logging_config import get_logger
from .utils import load_df
from .process_embeddings import process_embeddings

logger = get_logger(__name__)

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
    
    
def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', 'Question_Embedding_20240128.csv')
    
    logger.debug(f"Base directory set to: {base_dir}")
    logger.debug(f"CSV path for question embeddings constructed: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Successfully loaded CSV file with {len(df)} records from {csv_path}")
    except FileNotFoundError:
        logger.exception(f"CSV file not found at {csv_path}")
        return
    
    try:
        df_processed = validate_and_process_csv(csv_path, "question_embedding")
        logger.info(f"DataFrame processed successfully with {len(df_processed)} records")
        logger.debug(f"First few records of the processed DataFrame:\n{df_processed.head()}")
    except ValueError as e:
        logger.error(f"Failed to process embeddings: {e}")
        return


if __name__ == "__main__": 
    main()
