import pandas as pd
import json

df = pd.read_csv(r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\data\Question_Embedding_20240128.csv")
print(type(json.loads(df["info.json"][0])))

print(df.head())
df['info_dict'] = df['info.json'].apply(json.loads)
print(df.head())
normalized_df = pd.json_normalize(df['info_dict'])
print(normalized_df.head())
df = df.drop(['info.json', 'info_dict'], axis=1).join(normalized_df)
print((df["isAdaptive"] == "false").sum())

df.to_csv("Question_embedding_20240902.csv")