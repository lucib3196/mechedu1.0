from flask import Blueprint, Flask, render_template, session, redirect, url_for, jsonify, flash
from ...db_models.models import File, EduModule,Folder
import os 
from ast import literal_eval
from src.run_quizzes.run_module import generateAdaptive, run_generate_py,run_generate,read_file
import tempfile
from src.utils.plutilities import process_prairielearn_html
from flask_wtf.csrf import generate_csrf
view_modules_bp = Blueprint('view_modules_bp', __name__)


@view_modules_bp.route("/view_modules", methods=['GET', 'POST'])
def view_modules():
    modules = EduModule.query.all()
    module_data = []
    for module in modules:
        module_data.append({
            'id': module.id,
            'name': module.name,
        })
    
    # Debugging
    print(module_data)
    # Pass data to the template
    return render_template("module_selection.html", modules=module_data)

@view_modules_bp.route("/view_modules/<module_name><module_id>", methods=['GET', 'POST'])
def view_module_details(module_name,module_id):
    csrf_token = generate_csrf()
    module = EduModule.query.filter_by(id=module_id).first()
    folder_data = []
    for folder in module.folders:
        files_data = []
        for file in folder.files:
            files_data.append({
                'id': file.id,
                'filename': file.filename,
                'content': file.content.decode('utf-8', errors='ignore') if file.content else ''
            })
        folder_data.append({
            'id': folder.id,
            'folder_name': folder.name,
            'files': files_data
        })
    print(folder_data)

    return render_template("module_content.html", folder_data=folder_data,csrf_token=csrf_token)

@view_modules_bp.route("/view_modules/<folder_name>_<folder_id>", methods=['GET', 'POST'])
def view_folder(folder_name, folder_id):
    folder = Folder.query.filter_by(id=folder_id).first()

    if not folder:
        return "<h1>Folder not found</h1>", 404

    files_data = [{
        "filename": file.filename,
        "content": file.content
    } for file in folder.files]
    
    print("This is the files data", files_data)  # Debugging

    file_names = {file.get("filename") for file in files_data}

    # Determine file type
    file_type = determine_file_type(file_names)

    if file_type == "NonAdaptive":
        return "<h1>NonAdaptive</h1>"
    elif file_type == "Adaptive":
        session["files_data"] = [{"filename": file['filename']} for file in files_data]  # Store only filenames in session
        return redirect(url_for('view_modules_bp.view_adaptive_quiz', folder_name=folder_name, folder_id=folder_id))
    else:
        return "<h1>Lecture</h1>"


@view_modules_bp.route("/view_modules/<folder_name>_<folder_id>_adaptive", methods=['GET', 'POST'])
def view_adaptive_quiz(folder_name, folder_id):
    files_data = session.get("files_data")
    csrf_token = generate_csrf()

    if not files_data:
        return "<h1>No files data found in session</h1>", 404

    # Re-fetch file contents if needed
    folder = Folder.query.filter_by(id=folder_id).first()

    if not folder:
        return "<h1>Folder not found</h1>", 404

    # Retrieve full file data based on filenames stored in the session
    full_files_data = [{
        "filename": file.filename,
        "content": file.content.decode('utf-8', errors='ignore')  # Assuming content is binary
    } for file in folder.files if file.filename in {f['filename'] for f in files_data}]

    print(f'This is the full files data:\n {full_files_data}')  # Debugging

    with tempfile.TemporaryDirectory() as tmpdir:
        for file in full_files_data:
            print(f'This is the file \n {file}')
            
            # Create a full path for the temporary file
            temp_file_path = os.path.join(tmpdir,file.get("filename"))
            
            # Ensure the content is in bytes
            content = file.get("content")
            if isinstance(content, str):
                content = content.encode('utf-8')  # Convert string to bytes

            # Open the file in write-binary mode
            with open(temp_file_path, 'wb') as f:
                f.write(content)

            print(f"Temporary file created at: {temp_file_path}")
        print(type(tmpdir))
        print(os.listdir(tmpdir))
        quiz_name = folder.name
        print(quiz_name)
        files = os.listdir(tmpdir)
        target_file = 'server.py'
        if target_file in files:
            server_file_path = os.path.join(tmpdir, target_file)
            print(f"Found {target_file} at {server_file_path}")
            params = run_generate(server_file_path)
            print(f"Found params {params}\n")
            print(f'This is the type {type(params)}')
            print(params)
            question_html = read_file(os.path.join(tmpdir,"question.html"))
            solution_html = read_file(os.path.join(tmpdir,"question.html"))
            question_html_template, solution_html_template = process_prairielearn_html(question_html,solution_html,qdata=params,qname=quiz_name)
            print(question_html_template,solution_html_template)
        else:
            print(f"{target_file} not found in the temporary directory.")

    return render_template("question_base.html", quiz_name = quiz_name,question_html = question_html_template,csrf_token=csrf_token)



def determine_file_type(file_names):
    adaptive_files = {'question.html', 'server.js', 'server.py', 'solution.html', 'info.json'}
    nonadaptive_files = {'question.html', 'info.json'}

    if file_names == nonadaptive_files:
        return "NonAdaptive"
    elif file_names == adaptive_files:
        return "Adaptive"
    else:
        return "Lecture"




#     # Question Module Files
#     important_files =  {'question.html', 'server.js', 'server.py', 'solution.html', 'info.json'}
#     print("Inside" ,files_data)
#     # Check if any of the important files are present
#     if any(file in files_data for file in important_files):
#         return redirect(url_for('view_modules_bp.view_adaptive_quiz', folder_name=folder.name, files_data =files_data,folder_id=folder_id ))
#     return "This is lecture"

#     # files_data = []
#     # for file in folder.files:
#     #     files_data.append({
#     #             'id': file.id,
#     #             'filename': file.filename,
#     #             'content': file.content.decode('utf-8', errors='ignore') if file.content else ''
#     #         })
#     return f"These are the files {files_data}"

# @view_modules_bp.route("/view_modules/<folder_name>_<folder_id>_adaptive<files_data>", methods=['GET', 'POST'])
# def view_adaptive_quiz(folder_name, files_data,folder_id):
#     print(files_data)
#     # with tempfile.TemporaryDirectory() as tempdir:
#     #     quiz_path_with_contents = [os.path.join(tempdir, folder_name, file) for file in literal_eval(files_data)]
#     #     quiz_path = os.path.join(tempdir, folder_name)
#     #     print(quiz_path_with_contents)
#     #     print(type(quiz_path_with_contents[1]))
#     return f"Hi"