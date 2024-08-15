import os
import tempfile
from typing import Dict, Any
import json
import os
import io
import zipfile
from typing import List


def save_files_temp(question_title: str, files: Dict[str, Any]) -> str:
    """
    Saves files with their respective content to a temporary directory.

    This function creates a temporary directory, saves the provided files with their content 
    under a subdirectory named after `question_title`, and returns the path to the created directory.

    Args:
        question_title (str): The title of the question, which will be used as the name of the subdirectory.
        files (Dict[str, Any]): A dictionary where the keys are filenames (str) and the values are the corresponding file contents. 
                                The content can be either a string or a dictionary.

    Returns:
        str: The path to the directory where the files have been saved.

    Example:
        files = {
            "file1.txt": "This is the content of file1.",
            "file2.py": "print('Hello, World!')"
        }
        dir_path = save_files_temp("sample_question", files)
        # The function will create a temporary directory with the structure:
        # <tempdir>/sample_question/file1.txt
        # <tempdir>/sample_question/file2.py
    """
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_module_dir = os.path.join(temp_dir, question_title)
        os.makedirs(temp_module_dir, exist_ok=True)

        # Save the content to the directory
        for file_name, content in files.items():
            filepath = os.path.join(temp_module_dir, file_name)
            with open(filepath, "w") as file:
                if isinstance(content, dict):
                    file.write(json.dumps(content, indent=4))
                else:
                    file.write(str(content))
        
        print(f"Temporary directory created: {temp_module_dir}")
        return temp_module_dir
    except Exception as e:
        print(f"An error occurred while creating the temporary directory: {e}")
        return None

def create_zip_file(file_paths: List[str], base_dir: str) -> io.BytesIO:
    """
    Creates a zip file containing the specified files.

    Args:
        file_paths (List[str]): List of file paths to include in the zip file.
        base_dir (str): The base directory to use for relative paths in the zip file.

    Returns:
        io.BytesIO: A BytesIO object containing the zipped content.
    """
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.relpath(file_path, base_dir))
    memory_file.seek(0)
    return memory_file

def save_temp_dir_as_zip(temp_dir: str) -> io.BytesIO:
    """
    Saves the contents of the temporary directory to a zip file and returns it as a BytesIO object.

    Args:
        temp_dir (str): The path to the temporary directory.

    Returns:
        io.BytesIO: A BytesIO object containing the zipped content of the temporary directory.
    """
    # Verify if temp_dir exists and list its contents
    if not os.path.exists(temp_dir):
        print(f"Temporary directory does not exist: {temp_dir}")
        return None

    print(f"Temporary directory exists: {temp_dir}")
    print("Listing contents of the temp directory:")
    print(os.listdir(temp_dir))  # List the immediate contents of the directory

    # Collect all file paths in the temp directory
    file_paths = []
    print("Walking through the directory structure:")
    for root, dirs, files in os.walk(temp_dir):
        print(f"Current directory: {root}")
        print(f"Subdirectories: {dirs}")
        print(f"Files: {files}")
        for file in files:
            file_paths.append(os.path.join(root, file))
    
    # Check if file_paths collected any files
    if not file_paths:
        print("No files found in the directory to zip.")
        return None

    print(f"Files to be zipped: {file_paths}")
    
    # Use the provided create_zip_file function to create a zip file in memory
    zip_file = create_zip_file(file_paths, temp_dir)

    return zip_file