import requests
import bs4
from urllib.parse import urljoin
import json
from langchain_text_splitters import HTMLHeaderTextSplitter, HTMLSectionSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Check if a link is a GitHub link
def is_github_link(href: str) -> bool:
    return href.startswith("https://github.com/")

# Main function to scrape the webpage and process elements
def main():
    print('running')
    # Set to hold all GitHub links found
    all_links = set()
    
    # Original link to scrape
    original_link = "https://prairielearn.readthedocs.io/en/latest/elements/"
    
    # Send a GET request to the link
    html = requests.get(original_link)
    
    # Parse the HTML content
    soup = bs4.BeautifulSoup(html.text, 'html.parser')

    # Define the valid elements that we can render
    VALID_ELEMENTS: list[str] = [
        "pl-question-panel", "pl-number-input", "pl-checkbox", "pl-figure",
        "pl-integer-input", "pl-matching", "pl-matrix-component-input",
        "pl-matrix-input", "pl-multiple-choice", "pl-order-blocks",
        "pl-symbolic-input", "pl-units-input", "pl-matrix-latex", "pl-card", 
        "pl-answer-panel"
    ]

    # Modify the string so that it matches the id of the header
    VALID_ELEMENTS_EX = [(v + "-element") for v in VALID_ELEMENTS]

    # List to hold content for valid elements
    content = []

    # Find all h3 tags in the HTML
    h3_tags = soup.find_all("h3")

    # Extract information for each valid h3 tag
    for h3 in h3_tags:
        if h3.get("id") in VALID_ELEMENTS_EX:
            element_info = []
            element_info.append(h3)
            
            # Traverse sibling elements until the next h3 is found
            current_tag = h3.find_next_sibling()
            while current_tag and current_tag != h3.find_next("h3"):
                element_info.append(current_tag)
                
                # Extract and collect GitHub links
                extracted_links = current_tag.find_all("a")
                for link in extracted_links:
                    href = link.get("href")
                    if is_github_link(href):
                        all_links.add(href)
                
                current_tag = current_tag.find_next_sibling()
            
            content.append(element_info)

    # Convert the collected content into a single HTML string
    html_text = ""
    for c in content:
        for elem in c:
            html_text += str(elem)

    # Define headers to split the HTML content on
    headers_to_split_on = [("h3", "Header 3")]

    # Initialize the HTML section splitter
    html_splitter = HTMLSectionSplitter(headers_to_split_on)

    # Split the HTML text into sections and store the result
    all_docs = []
    all_docs.extend(html_splitter.split_text(html_text))

    # Create a vector store from the documents and embeddings
    vectorstore = Chroma.from_documents(all_docs, OpenAIEmbeddings(), persist_directory="./pl_chroma_db")


# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
