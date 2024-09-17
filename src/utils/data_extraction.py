import os
from bs4 import BeautifulSoup
import pandas as pd
path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu\website\quizzes"


all_files = []
unique_tags = []

# Step 1: Collect all valid file paths
for root, dirs, files in os.walk(path):
    valid_file_names = ["question.html"]
    for file in files:
        if file in valid_file_names:
            all_files.append(os.path.join(root, file))
print(len(all_files))


valid_tags = ["pl-question-panel","pl-number-input","pl-multiple-choice","pl-answer","pl-choice","pl-checkbox"]
# Step 2: Process each file and collect tags
count = 0
for file in all_files:
    with open(file, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        all_tags = soup.find_all(True)
        set_tags = set()
        for tag in all_tags:
            if tag.name.startswith("pl"):
                # Check if the tag already exists in the unique_tags list
                existing_tag = next((entry for entry in unique_tags if entry["tag_name"] == tag.name), None)

                if tag.name in set_tags:
                    continue
                else:
                    set_tags.add(tag.name)

                if existing_tag:
                    # If tag already exists, increment the count
                    existing_tag["count"] += 1
                else:
                    # If tag doesn't exist, add it with a count of 1
                    unique_tags.append({
                        "tag_name": tag.name,
                        "html": str(tag),
                        "file_ref": file,
                        "count": 1
                    })
        if all(tag in valid_tags for tag in set_tags):
            count+=1
print(count)
        

# Step 3: Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(unique_tags, columns=["tag_name", "html", "file_ref", "count"])
print(df.sort_values("count",ascending=False))

# Step 4: Print or save the DataFrame
# df.to_csv("unique_tags.csv")
