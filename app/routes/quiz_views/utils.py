from ...db_models.models import Folder
from typing import Union,List, Dict
from flask import session
import json
from typing import Optional

from src.logging_config.logging_config import get_logger
# Initialize the logger
logger = get_logger(__name__)

def retrieve_files_session(module_name: str, folder_name: str, folder_id: int) -> Union[List[Dict[str, str]], tuple]:
    """
    Retrieves file data from the session and filters it based on the folder content.

    This function fetches the file data stored in the user's session. If the session does not contain
    the expected data, it returns an error message and a 404 status code. The function then retrieves
    the corresponding folder from the database, decodes the content of the files (assuming they are stored 
    as binary), and returns a list of dictionaries containing the filenames and their respective content.

    Args:
        module_name (str): The name of the module to which the files belong.
        folder_name (str): The name of the folder containing the files.
        folder_id (int): The unique identifier for the folder in the database.

    Returns:
        Union[List[Dict[str, str]], tuple]: A list of dictionaries containing the filename and decoded content
                                            of each file, or a tuple with an error message and a 404 status code 
                                            if no files data is found in the session.
    """
    files_data = session.get("files_data")
    print(f"Inside the retrieve_files_session {files_data}")
    if not files_data:
        return "<h1>No files data found in session</h1>", 404
    
    folder = Folder.query.filter_by(id=folder_id).first()
    if not folder:
        return "<h1>Folder not found</h1>", 404
    
    full_files_data = [{
        "filename": file.filename,
        "content":decode_content(file.content)  # Assuming content is binary
    } for file in folder.files if file.filename in {f['filename'] for f in files_data}]
    
    return full_files_data


from typing import Tuple, List, Dict, Union
from flask import session

def retrieve_files_folder(folder_id: int) -> Union[Tuple[str, List[Dict[str, str]]], str]:
    """
    Retrieve the name of the current folder and its associated files from the database.

    This function retrieves the folder ID from the current session, fetches the corresponding
    folder from the database, and returns the folder's name along with the list of files contained
    within the folder. Each file's data includes the filename and the content decoded as a UTF-8 string.

    Returns:
        Union[Tuple[str, List[Dict[str, str]]], str]: 
            - If successful, returns a tuple containing:
                - folder_name (str): The name of the folder.
                - full_files_data (List[Dict[str, str]]): A list of dictionaries, each containing:
                    - "filename" (str): The name of the file.
                    - "content" (str): The content of the file, decoded as a UTF-8 string.
            - If an error occurs, returns a descriptive error message as a string.
    """
    
    if not folder_id:
        raise "Error: Folder ID not found in session."

    folder = Folder.query.filter_by(id=folder_id).first()
    
    if not folder:
        return f"Error: Folder with ID {folder_id} not found."
    
    folder_name = folder.name
    full_files_data = [
        {
            "filename": file.filename,
            "content": decode_content(file.content)
        }
        for file in folder.files
    ]
    
    return folder_name, full_files_data


def decode_content(content: str) -> dict|str|None:
    """
    Decodes the given content string, handling both hex-encoded data and plain strings.

    If the input is a hex-encoded string (starts with '\\x'), it decodes it into a
    readable format. If the decoded content is valid JSON, it parses and returns it
    as a dictionary. If the content is already a plain string, it attempts to parse
    it as JSON or returns the string as-is.

    Args:
        content (str): The input content to decode. Can be a hex-encoded string (e.g., '\\x7b...') 
                       or a plain string.

    Returns:
        Optional[dict]: Returns the parsed JSON as a dictionary if successful, or the decoded 
                        plain string. Returns None if the decoding or parsing fails.
    """
    try:
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        if content.startswith("\\x"):
            decoded = bytes.fromhex(content.replace("\\x", "")).decode("utf-8")
        else:
            # Content is already a string
            decoded = content
        
        # Try parsing as JSON
        try:
            return json.loads(decoded)
        except json.JSONDecodeError:
            # Not JSON, return as plain string
            return decoded
    except Exception as e:
        print(f"Error decoding content: {e}")
        return None

