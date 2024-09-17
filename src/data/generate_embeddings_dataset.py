import pandas as pd
from src.credentials import api_key
from src.data_handler.generate_embeddings import GenerateEmbeddings

csv_path = r"src\data\question_embeddings_2024_9_11.csv"
df = pd.read_csv(csv_path)
filtered_df= df.iloc[0]
print(df.columns)
print(df["question_embedding"].iloc[:5])
print(df["embeddings-3-small"].iloc[:5])

print(df.iloc[0]["question"])

embedding_gen = GenerateEmbeddings(api_key,model="text-embedding-3-small",temperature=0)
print(embedding_gen.get_embeddings_sync(df.iloc[0]["question"]))