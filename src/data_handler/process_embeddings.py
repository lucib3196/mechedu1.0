import pandas as pd
import ast

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
        print(f"Processed Embedding Columns {embedding_column} succesfully")
        return df
    except ValueError as e:
        raise ValueError (f"Failed to process {embedding_column} column from dataframe") from e

def main():
    return None
if __name__ =="__main__":
    main()