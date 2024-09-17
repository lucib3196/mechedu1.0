import pandas as pd
import os


path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu\website\quizzes"


data = []
for root, dirs, files in os.walk(path):
    question_data ={}
    for file in files:
        if file =="question.html":
            full_path = os.path.join(root,file)
            with open(full_path,"rb") as f:
                content = f.read()
                question_data["question.html"] = content.decode("utf-8")
                data.append(question_data)
df = pd.DataFrame(data)
print(df.head())