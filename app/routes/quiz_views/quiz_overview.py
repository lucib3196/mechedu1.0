# Standard Library Imports
import os
import tempfile
import zipfile
import io
import json
from io import BytesIO

# Third-Party Imports
from flask import (
    Blueprint, render_template, request, send_file, jsonify, session,
    redirect, url_for, Response, flash
)
from src.logging_config.logging_config import get_logger
# Initialize the logger
logger = get_logger(__name__)

# Local Application Imports
from ...db_models.models import File, EduModule, Folder, db
from .utils import retrieve_files_session, retrieve_files_folder
from src.utils.file_handler import create_zip_file
from ...form.forms import UPDATE_CODE,DOWNLOAD 

quiz_overview_bp = Blueprint('quiz_overview_bp', __name__)
# This is perfect as is 
@quiz_overview_bp.route("/quiz_overview/<folder_id>/actions", methods=['GET', 'POST'])
def modules_action(folder_id):
    folder = Folder.query.filter_by(id=folder_id).first_or_404(description="Quiz Not Found")
    session["folder_id"] = folder.id
    return render_template('module_actions.html',folder=folder)

@quiz_overview_bp.route('/edit_code/<int:fileid>', methods=['GET', 'POST'])
def edit_code(fileid):
    # Retrieve the file from the database using its ID
    file = File.query.filter_by(id=fileid).first_or_404(description="File Not Found")
    session["fileid"] = file.id
    code_content = file.content.decode('utf-8')

    language_map = {
        "py":"python",
        "js":"javascript",
        "html":"html"
    }
    extension = file.filename.split('.')[1]
    return render_template('edit_code.html', code = code_content, data = json.dumps(language_map.get(extension)))

@quiz_overview_bp.route('/save_code', methods=['GET', 'POST','FETCH'])
def save_code():
    data = request.get_json()
    updated_code = data.get('code')
    fileid = session.get("fileid","")

    old_file = File.query.filter_by(id=fileid).first_or_404(description="File Not Found")
    old_file.content = updated_code.encode('utf-8')
    db.session.commit()
    flash('Code saved successfully!', 'success')
    return redirect(url_for('quiz_overview_bp.edit_code', fileid=fileid))

# All This needs to be fixed eventually with databases and the info.json file 

def determine_file_type(file_names:dict)->str:
    adaptive_files = {'question.html', 'server.js', 'server.py', 'solution.html', 'info.json'}
    nonadaptive_files = {'question.html', 'info.json'}

    if file_names == nonadaptive_files:
        return "NonAdaptive"
    elif file_names == adaptive_files:
        return "Adaptive"
    else:
        return "Lecture"
@quiz_overview_bp.route('/quiz_overview/<int:folder_id>', methods=['GET', 'POST'])
def render_content(folder_id):
    # Retrieve the folder
    folder = Folder.query.filter_by(id=folder_id).first_or_404(description="Quiz Not Found")
    
    # Try to retrieve the metadata file and lecture file
    metadata_file = File.query.filter_by(folder_id=folder_id, filename="info.json").first()
    lecture_file = File.query.filter_by(folder_id=folder_id, filename="lecture.html").first()

    # Case 1: Adaptive/Non-Adaptive Content based on metadata
    if metadata_file:
        logger.info(f'Metadata file: {metadata_file}')
        # Load the metadata content
        metadata = json.loads(metadata_file.content.decode('utf-8'))
        is_adaptive = metadata.get("isAdaptive")
        
        # Adaptive Content
        if is_adaptive:
            return redirect(url_for('adaptive_quiz_bp.render_adaptive_quiz', folder_id=folder_id))
        
        # Non-Adaptive Content
        else:
            return redirect(url_for('non_adaptive_quiz_bp.render_non_adaptive_quiz', folder_id=folder_id))
    # Case 2: Lecture Content (HTML file)
    elif lecture_file:
        # Render the lecture HTML file content
        lecture_content = lecture_file.content.decode('utf-8')
        return render_template('lecture.html', lecture=lecture_content)
    
    # Case 3: No content found
    else:
        return "No valid content found for this folder", 404



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



