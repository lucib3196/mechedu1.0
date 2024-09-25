import requests
import bs4
from urllib.parse import urljoin
import json
from langchain_text_splitters import HTMLHeaderTextSplitter
from langchain_text_splitters import HTMLSectionSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
def is_github_link(href:str):
  return href.startswith("https://github.com/")


all_links = set()
original_link = "https://prairielearn.readthedocs.io/en/latest/elements/"
html = requests.get(original_link)
soup = bs4.BeautifulSoup(html.text, 'html.parser')
# Define the valid elements that we can render
VALID_ELEMENTS: list[str] = [
    "pl-question-panel", "pl-number-input", "pl-checkbox", "pl-figure",
    "pl-integer-input", "pl-matching", "pl-matrix-component-input",
    "pl-matrix-input", "pl-multiple-choice", "pl-order-blocks",
    "pl-symbolic-input", "pl-units-input","pl-matrix-latex","pl-card","pl-answer-panel"
]
# Modify the string so that it matches the id of the header
VALID_ELEMENTS_EX = [(v + "-element") for v in VALID_ELEMENTS]

content =[]
h3_tags = soup.find_all("h3")
for h3 in h3_tags:
  if h3.get("id") in VALID_ELEMENTS_EX:
    element_info =[]
    element_info.append(h3)
    current_tag = h3.find_next_sibling()
    while current_tag and current_tag != h3.find_next("h3"):
      element_info.append(current_tag)
      extracted_links = current_tag.find_all("a")
      for link in extracted_links:
        href = link.get("href")
        if is_github_link(href):
          all_links.add(href)
      current_tag = current_tag.find_next_sibling()
    content.append(element_info)
html_text= ""
for c in content:
  for elem in c:
    html_text += str(elem)



headers_to_split_on = [
    ("h3", "Header 3"),
]
html_splitter = HTMLSectionSplitter(
    headers_to_split_on
)
all_docs = []
all_docs.extend(html_splitter.split_text(html_text))


vectorstore = Chroma.from_documents(all_docs, OpenAIEmbeddings(), persist_directory="./pl_chroma_db")