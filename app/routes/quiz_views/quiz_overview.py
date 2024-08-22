# Standard Library Imports
import os
import tempfile
import zipfile
from typing import List
from ...db_models.models import File, EduModule, Folder
import io

# Third-Party Imports
from flask import Blueprint, render_template, request, send_file, jsonify, session, redirect, url_for

# Local Application Imports
from ...db_models.models import Folder
from .utils import retrieve_files_session
from src.utils.file_handler import create_zip_file


quiz_overview_bp = Blueprint('quiz_overview_bp', __name__)

def determine_file_type(file_names):
    adaptive_files = {'question.html', 'server.js', 'server.py', 'solution.html', 'info.json'}
    nonadaptive_files = {'question.html', 'info.json'}

    if file_names == nonadaptive_files:
        return "NonAdaptive"
    elif file_names == adaptive_files:
        return "Adaptive"
    else:
        return "Lecture"
    
@quiz_overview_bp.route("/quiz_overview/<module_name><folder_name>_<folder_id>", methods=['GET', 'POST'])
def module_details(module_name, folder_name, folder_id):
    folder = Folder.query.filter_by(id=folder_id).first()

    if not folder:
        return "<h1>Quiz Not Found</h1>", 404
    
    files_data = [{
        "filename": file.filename,
        "content": file.content
    } for file in folder.files]

    file_names = {file.get("filename") for file in files_data}

    file_type = determine_file_type(file_names)

    if file_type == "NonAdaptive":
        return "<h1>NonAdaptive</h1>"
    elif file_type == "Adaptive":
        session["files_data"] = [{"filename": file['filename']} for file in files_data]  # Store only filenames in session
        return redirect(url_for("adaptive_quiz_bp.render_adaptive_quiz", module_name=module_name, folder_name=folder_name, folder_id=folder_id))
    else:
        session["files_data"] = [{"filename": file['filename']} for file in files_data]
        # Decode the bytes content to a string
        content = files_data[0].get("content").decode('utf-8', errors='ignore')
        
        # Render the template with the escaped content
        return render_template('lecture.html', lecture=content, module_name=module_name, folder_name=folder_name, folder_id=folder_id)
    

@quiz_overview_bp.route("/retrieve_modules/download_all", methods=['GET', 'POST'])
def download_all_modules():
    """
    Downloads a combined ZIP file containing ZIP files for all modules and folders in the session.

    The function retrieves folder data from the session, processes each folder to create individual ZIP files, 
    and then combines these ZIP files into a single downloadable ZIP file.

    Returns:
        Response: A Flask response object that triggers the download of the combined ZIP file.
    """
    folder_data = session.get("module_id")
    
    if not folder_data:
        return "No folder data found in session", 400
    
    combined_zip_buffer = io.BytesIO()

    with zipfile.ZipFile(combined_zip_buffer, 'w') as combined_zip:
        for folder in folder_data:
            full_files_data = retrieve_files_session("test", folder.get("folder_name"), folder.get("id"))
            file_paths = []
            
            with tempfile.TemporaryDirectory() as tmpdir:
                for file in full_files_data:
                    # Create a full path for the temporary file
                    tempfile_path = os.path.join(tmpdir, file.get("filename"))
                    content = file.get("content", "")
                    
                    # Ensure the content is in bytes, encoding if necessary
                    if isinstance(content, str):
                        content = content.encode('utf-8')  # Convert string to bytes
                    
                    # Write the content to the temporary file
                    with open(tempfile_path, 'wb') as f:
                        f.write(content)
                    
                    print(f"Temporary file created at: {tempfile_path}")  # Debugging output
                    
                    # Add the temporary file path to the list of files to be zipped
                    file_paths.append(tempfile_path)
                
                # Create a ZIP file for the current folder and store it in memory
                folder_zip_buffer = io.BytesIO()
                with zipfile.ZipFile(folder_zip_buffer, 'w') as folder_zip:
                    for file_path in file_paths:
                        folder_zip.write(file_path, os.path.basename(file_path))
                
                # Write the in-memory ZIP file to the combined ZIP file
                folder_zip_filename = f"{folder.get('folder_name')}_{folder.get('id')}.zip"
                folder_zip_buffer.seek(0)
                combined_zip.writestr(folder_zip_filename, folder_zip_buffer.read())
    
    combined_zip_buffer.seek(0)
    return send_file(combined_zip_buffer, mimetype='application/zip', as_attachment=True, download_name='all_modules.zip')

@quiz_overview_bp.route("/quiz_overview/<module_name><folder_name>_<folder_id>/download", methods=['GET', 'POST'])
def download_module(module_name: str, folder_name: str, folder_id: int):
    """
    Downloads a ZIP file containing all the files associated with a module and folder.

    This function retrieves the files from the user's session, writes them to a temporary directory, 
    creates a ZIP file containing the files, and then sends the ZIP file as a downloadable response.

    Args:
        module_name (str): The name of the module associated with the files.
        folder_name (str): The name of the folder containing the files.
        folder_id (int): The unique identifier for the folder in the database.

    Returns:
        Response: A Flask response object that triggers the download of the ZIP file.
    """
    
    # Retrieve the files data from the session based on module and folder information
    full_files_data = retrieve_files_session(module_name, folder_name, folder_id)
    
    # Query the folder object from the database using the folder_id
    folder = Folder.query.filter_by(id=folder_id).first()
    
    file_paths = []  # List to store the paths of temporary files
    
    # Create a temporary directory to store the files before zipping
    with tempfile.TemporaryDirectory() as tmpdir:
        for file in full_files_data:
            # Create a full path for the temporary file
            tempfile_path = os.path.join(tmpdir, file.get("filename"))
            content = file.get("content", "")
            
            # Ensure the content is in bytes, encoding if necessary
            if isinstance(content, str):
                content = content.encode('utf-8')  # Convert string to bytes
            
            # Write the content to the temporary file
            with open(tempfile_path, 'wb') as f:
                f.write(content)
            
            print(f"Temporary file created at: {tempfile_path}")  # Debugging output
            
            # Add the temporary file path to the list of files to be zipped
            file_paths.append(tempfile_path)
        
        # Create a ZIP file from the list of temporary file paths
        zip_file = create_zip_file(file_paths)
        
        # Send the ZIP file as a downloadable response
        return send_file(zip_file, mimetype='application/zip', as_attachment=True, download_name=f'{folder.name}.zip')