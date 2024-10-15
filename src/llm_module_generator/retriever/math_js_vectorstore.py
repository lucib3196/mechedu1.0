import requests
import bs4
from urllib.parse import urljoin
from langchain_text_splitters import HTMLHeaderTextSplitter
from langchain_text_splitters import HTMLSectionSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

import requests
import bs4
from urllib.parse import urljoin
from typing import Set

# Code should only be ran once
## Creates the chroma.db for rag
def is_href_invalid(href: str) -> bool:
    """
    Checks if the href is an invalid link based on specific conditions.
    
    Args:
        href (str): The link to check.
    
    Returns:
        bool: True if the link is invalid, otherwise False.
    """
    if (href.startswith("https://en.wikipedia.org") or
        href.startswith("https://github.com") or
        href.startswith("#") or
        ('#' in href)):
        return True
    return False


def extract_all_links(link: str) -> Set[str]:
    """
    Recursively extracts all unique links from a given webpage and its child pages.
    
    Args:
        link (str): The URL of the webpage to extract links from.
    
    Returns:
        Set[str]: A set of all unique links found.
    """
    all_links = set()
    html = requests.get(link)
    soup = bs4.BeautifulSoup(html.text, 'html.parser')
    div_tags = soup.find_all("div")
    
    for tag in div_tags:
        if tag.attrs.get("id") == "content":
            for a in tag.find_all("a"):
                href = a.attrs.get("href")
                
                if href is not None and not is_href_invalid(href):
                    # Check if the href is a full URL
                    if not href.startswith("http://") and not href.startswith("https://"):
                        # Append the base URL if it's a relative link
                        full_link = urljoin(link, href)
                    else:
                        full_link = href
                    
                    if full_link not in all_links:
                        all_links.add(full_link)
                        extract_all_links(full_link)
    
    return all_links
import requests

def check_and_return_html(url: str) -> str:
    """
    Attempts to request the HTML content from a given URL, handling common errors.

    Args:
        url (str): The URL to make the request to.

    Returns:
        str: The HTML content of the webpage if the request is successful. If the request fails, 
        it prints an error message and returns an empty string.
    """
    # Fix any backslashes in the URL by replacing them with forward slashes
    url = url.replace('\\', '/')

    try:
        # Attempt to make a request to the URL
        response = requests.get(url)

        # Check if the response status code is OK (200)
        if response.status_code == 200:
            print(f"Success: The URL '{url}' is valid and reachable.")
            return response.text
        else:
            print(f"Error: Received status code {response.status_code} from '{url}'.")
            return ""

    except requests.exceptions.MissingSchema:
        print(f"Error: The URL '{url}' is invalid (possibly missing 'http://' or 'https://').")
    except requests.exceptions.RequestException as e:
        # Handle other exceptions like connection errors
        print(f"Error: Could not reach '{url}'. Exception details: {e}")

    return ""


def main():
    """
    Main function to extract links, split the content of the webpages,
    and store the results in a vectorstore for future use.
    """
    
    # Base URL to extract links from
    original_link = "https://mathjs.org/docs/index.html"
    
    # Extract all links from the base URL
    all_links = extract_all_links(original_link)
    
    # Headers to split the HTML content on
    headers_to_split_on = [
        ("h1", "Header 1"),
    ]
    
    # Initialize the HTML splitter with the specified headers
    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on)
    
    # Convert the set of links into a list
    all_links = list(all_links)
    
    # Initialize an empty list to store the document contents
    all_docs = []
    
    # Loop over each link, get the HTML content, split it, and store the results
    for i in range(len(all_links)):
        try:
            # Fetch the HTML content and split it into sections
            html_content = check_and_return_html(all_links[i])
            all_docs.extend(html_splitter.split_text(html_content))
        except Exception as e:
            print(f"Error processing {all_links[i]}: {e}")
    
    # Store the processed documents in a vectorstore using Chroma
    vectorstore = Chroma.from_documents(
        all_docs, 
        OpenAIEmbeddings(), 
        persist_directory="./chroma_db"
    )

# Call the main function
if __name__ == "__main__":
    main()