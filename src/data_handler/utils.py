import os
import pandas as pd
from typing import List

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

def is_valid_column(df:pd.DataFrame, column_to_check:str)->bool:
    """Checks to see if column is in dataframe

    Args:
        df (pd.DataFrame): dataframe
        column_to_check (str): column to check 

    Returns:
        bool: returns true if column in dataframe
    """
    return (column_to_check in df.columns)

def is_valid_columns(df:pd.DataFrame, columns: List[str])-> bool:
    invalid_columns = [column for column in columns if not is_valid_column(df, column)]
    if invalid_columns:
        print(f"Columns {[column for column in invalid_columns]} are not valid.")
        return False
    else:
        return True
    