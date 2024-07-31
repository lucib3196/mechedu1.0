import pandas as pd
import ast

def process_embeddings(df:pd.DataFrame, embedding_column:str):
    try:
        df[embedding_column] = df[embedding_column].apply(ast.literal_eval)
        df[embedding_column] = df[embedding_column].apply(lambda x: [float(i) for i in x])
        print(f"DEBUG: Processed Embedding Columns {embedding_column} succesfully")
    except ValueError as e:
        raise ValueError (f"Failed to process {embedding_column} column from dataframe") from e
    return df

## Testing 
# csv_path = r"src\data\Question_Embedding_20240128.csv"
# embedding_column = "question_embedding"
# df = pd.read_csv(csv_path)
# print(df.head())
# df = process_embeddings(df,embedding_column)