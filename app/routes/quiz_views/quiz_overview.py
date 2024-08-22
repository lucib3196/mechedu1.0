# Standard Library Imports
import os
import tempfile
import zipfile
import io
import json
from typing import List
from ast import literal_eval
from io import BytesIO

# Third-Party Imports
from flask import Blueprint, render_template, request, send_file, jsonify, session, redirect, url_for, Response

# Local Application Imports
from ...db_models.models import File, EduModule, Folder
from .utils import retrieve_files_session, retrieve_files_folder
from src.utils.file_handler import create_zip_file


quiz_overview_bp = Blueprint('quiz_overview_bp', __name__)

# This needs to be fixed eventually with databases and the info.jsonm file 
def determine_file_type(file_names:dict)->str:
    adaptive_files = {'question.html', 'server.js', 'server.py', 'solution.html', 'info.json'}
    nonadaptive_files = {'question.html', 'info.json'}

    if file_names == nonadaptive_files:
        return "NonAdaptive"
    elif file_names == adaptive_files:
        return "Adaptive"
    else:
        return "Lecture"
    
@quiz_overview_bp.route("/quiz_overview/<folder_id>", methods=['GET', 'POST'])
def module_details(folder_id):
    folder = Folder.query.filter_by(id=folder_id).first()
    if not folder:
        return "<h1>Quiz Not Found</h1>", 404
    # Get the name of the files
    files_names = [{
        "filename": file.filename,
    }for file in folder.files]
    # Store folder information  in session
    session["folder_id"] = folder.id
    session["files_names"] = files_names
    
    file_names_filter = {filename.get("filename") for filename in files_names}
    file_type = determine_file_type(file_names_filter)

    if file_type == "NonAdaptive":
        return "<h1>NonAdaptive</h1>"
    elif file_type == "Adaptive":
        return redirect(url_for("adaptive_quiz_bp.render_adaptive_quiz"))
    else:
        # Decode the bytes content to a string
        # content = files_data[0].get("content").decode('utf-8', errors='ignore')
        
        # Render the template with the escaped content
        # return render_template('lecture.html', lecture=content, module_name=module_name, folder_name=folder_name, folder_id=folder_id)
        return "Hello"
    
@quiz_overview_bp.route("/quiz_overview/download", methods=['GET', 'POST'])
def download_module():
    folder_id = session["folder_id"]
    print(folder_id)
    folder_name, full_files_data = retrieve_files_folder(folder_id)
    tempfile_paths = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for file in full_files_data:
            tempfile_path = os.path.join(tmpdir, file.get("filename"))
            content = file.get("content", "")
            # Ensure the content is in bytes, encoding if necessary
            if isinstance(content, str):
                content = content.encode('utf-8')  # Convert string to bytes

            with open(tempfile_path, 'wb') as f:
                f.write(content)
            print(f"Temporary file created at for downloading: {tempfile_path}")  # Debugging output

            tempfile_paths.append(tempfile_path)

        zip_file = create_zip_file(tempfile_paths)
        return send_file(zip_file, mimetype='application/zip', as_attachment=True, download_name=f'{folder_name}.zip')
    
@quiz_overview_bp.route("/retrieve_modules/download_all", methods=['GET', 'POST'])
def download_all_modules():
    """
    Downloads a combined ZIP file containing ZIP files for all modules and folders in the session.

    The function retrieves folder data from the session, processes each folder to create individual ZIP files, 
    and then combines these ZIP files into a single downloadable ZIP file.

    Returns:
        Response: A Flask response object that triggers the download of the combined ZIP file.
    """
    folder_data = session.get("folder_data", [])
    print("Downloading all")
    
    # Create an in-memory ZIP file
    master_zip_buffer = BytesIO()
    
    with zipfile.ZipFile(master_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as master_zip:
        for folder in folder_data:
            folder_name = folder.get("folder_name")
            folder_id = folder.get("id")
            print(f"Processing folder: {folder_name}_{folder_id}")

            # Assuming retrieve_files_folder takes folder_id as an argument
            folder_name, full_files_data = retrieve_files_folder(folder_id)
            print(f"Files in folder {folder_name}: {full_files_data}")

            # Create a folder-specific ZIP in memory
            folder_zip_buffer = BytesIO()
            with zipfile.ZipFile(folder_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as folder_zip:
                for file in full_files_data:
                    filename = file.get("filename")
                    content = file.get("content", "").encode('utf-8') if isinstance(file.get("content", ""), str) else file.get("content")
                    
                    # Add file to folder-specific ZIP
                    folder_zip.writestr(filename, content)
                    print(f"Added {filename} to folder ZIP")

            # Move to the beginning of the BytesIO buffer before writing it into the master ZIP
            folder_zip_buffer.seek(0)
            master_zip.writestr(f"{folder_name}_{folder_id}.zip", folder_zip_buffer.read())
            print(f"Added {folder_name}_{folder_id}.zip to master ZIP")

    # Finalize the in-memory ZIP file
    master_zip_buffer.seek(0)
    
    return send_file(
        master_zip_buffer, 
        mimetype='application/zip', 
        as_attachment=True, 
        download_name="all_modules.zip"
    )



