# Standard Library Imports
import os
import tempfile

# Third-Party Imports
from flask import Blueprint, render_template, session, redirect, url_for

# Local Application Imports
from src.run_quizzes.run_module import generateAdaptive, run_generate_py, run_generate, read_file
from src.utils.plutilities import process_prairielearn_html
from ...db_models.models import Folder
from .utils import retrieve_files_session


adaptive_quiz_bp = Blueprint('adaptive_quiz_bp', __name__)

@adaptive_quiz_bp.route("/quiz_overview/<module_name><folder_name>_<folder_id>_adaptive", methods=['GET', 'POST'])
def render_adaptive_quiz(module_name, folder_name, folder_id):
    # This needs to be fixed evenetually
    folder = Folder.query.filter_by(id=folder_id).first()
    full_files_data = retrieve_files_session(module_name, folder_name,folder_id)

    with tempfile.TemporaryDirectory() as tmpdir:
        for file in full_files_data:
            # Create a full path for the temporary file
            tempfile_path = os.path.join(tmpdir,file.get("filename"))

            # Ensure that the content in in bytes
            content = file.get("content","")
            if isinstance(content, str):
                content = content.encode('utf-8')  # Convert string to bytes
            # Writes content to file
            with open(tempfile_path, 'wb') as f:
                f.write(content)
            print(f"Temporary file created at: {tempfile_path}") # Debug
        # print(f"This is the folder name {folder_name}")
        quiz_name = folder.name
        server_file = os.path.join(tmpdir, "server.js")
        params = run_generate(server_file)
        question_html = read_file(os.path.join(tmpdir,"question.html"))
        solution_html = read_file(os.path.join(tmpdir,"question.html"))
        question_html_template, solution_html_template = process_prairielearn_html(question_html,solution_html,qdata=params,qname=quiz_name)
        # print(question_html_template,solution_html_template)

    return render_template("question_base.html", quiz_name = quiz_name,question_html = question_html_template, module_name=module_name, folder_name=folder_name, folder_id=folder_id)

