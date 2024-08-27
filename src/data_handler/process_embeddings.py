import pandas as pd
import ast
import os 
from ..logging_config.logging_config import get_logger

logger = get_logger(__name__)

def process_embeddings(df: pd.DataFrame, embedding_column: str) -> pd.DataFrame:
    """Converts embedding column to float values

    Args:
        df (pd.DataFrame): DataFrame to be processed
        embedding_column (str): Name of the question embeddings

    Raises:
        ValueError: Error in processing embeddings

    Returns:
        pd.DataFrame: DataFrame after being processed
    """
    try:
        df[embedding_column] = df[embedding_column].apply(ast.literal_eval)
        df[embedding_column] = df[embedding_column].apply(lambda x: [float(i) for i in x])
        logger.info(f"Processed embedding column '{embedding_column}' successfully")
        return df
    except KeyError as e:
        logger.exception(f"Failed to process '{embedding_column}'. Not a valid name found in DataFrame.")
        raise ValueError(f"Column '{embedding_column}' not found in DataFrame") from e
    
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
        df_processed = process_embeddings(df, "question_embedding")
        logger.info(f"DataFrame processed successfully with {len(df_processed)} records")
        logger.debug(f"First few records of the processed DataFrame:\n{df_processed.head()}")
    except ValueError as e:
        logger.error(f"Failed to process embeddings: {e}")
        return


if __name__ == "__main__": 
    main()
