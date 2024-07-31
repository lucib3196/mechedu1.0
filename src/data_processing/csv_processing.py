import pandas as pd
import os
import ast

def isvalid_csv(csv_path: str) -> bool:
    """
    Checks if the given path is a valid CSV file.

    Parameters:
    - csv_path (str): The path to the CSV file.

    Returns:
    - bool: True if the file exists and is a valid CSV, False otherwise.
    """
    return os.path.isfile(csv_path)
        
def load_df(csv_path: str) -> pd.DataFrame:
    """
    Loads a CSV file into a DataFrame if the file is valid.

    Parameters:
    - csv_path (str): The path to the CSV file.

    Returns:
    - pd.DataFrame: The loaded DataFrame, or None if the file is not valid.
    """
    if isvalid_csv(csv_path):
        try:
            return pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            print(f"Error: The file at {csv_path} is empty.")
        except pd.errors.ParserError:
            print(f"Error: The file at {csv_path} could not be parsed.")
        except Exception as e:
            print(f"Error: An unexpected error occurred while reading the CSV file: {e}")
    else:
        print(f"Error: The file path {csv_path} is not valid.")
    return None
    
def process_embeddings(df:pd.DataFrame, embedding_column:str)->pd.DataFrame:
    """Converts embedding column to float values

    Args:
        df (pd.DataFrame): dataframe to be processed
        embedding_column (str): name of the question embeddings

    Raises:
        ValueError: error in processing embeddings

    Returns:
        df (pd.DataFrame): dataframe after being processed
    """
    try:
        df[embedding_column] = df[embedding_column].apply(ast.literal_eval)
        df[embedding_column] = df[embedding_column].apply(lambda x: [float(i) for i in x])
        print(f"INFO: Processed Embedding Columns {embedding_column} succesfully")
        return df
    except ValueError as e:
        raise ValueError (f"Failed to process {embedding_column} column from dataframe") from e
    
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
    
    
# ## Testing 
# csv_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1.0\src\data\Question_Embedding_20240128.csv"
# df = validate_and_process_csv(csv_path,embedding_column="question_embedding")
# df.head()