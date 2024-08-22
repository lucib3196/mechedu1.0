# Standard Library Imports
import os
import tempfile
import traceback

# Third-Party Imports
from flask import Blueprint, render_template, session, redirect, url_for, flash

# Local Application Imports
from src.run_quizzes.run_module import generateAdaptive, run_generate_py, run_generate, read_file
from src.utils.plutilities import process_prairielearn_html
from ...db_models.models import Folder
from .utils import retrieve_files_folder

# Blueprint Definition
adaptive_quiz_bp = Blueprint('adaptive_quiz_bp', __name__)


@adaptive_quiz_bp.route("/quiz_overview/_adaptive", methods=['GET', 'POST'])
def render_adaptive_quiz():
    try:
        folder_name, full_files_data = retrieve_files_folder()
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in full_files_data:
                tempfile_path = os.path.join(tmpdir, file.get("filename"))
                content = file.get("content", "")
                if isinstance(content, str):
                    content = content.encode('utf-8')  # Convert string to bytes
                with open(tempfile_path, "wb") as f:
                    f.write(content)
                print(f"Temporary file created at: {tempfile_path}")  # Debug
            quiz_name = folder_name
            server_file = os.path.join(tmpdir, "server.js")
            params = run_generate(server_file)
            question_html = read_file(os.path.join(tmpdir, "question.html"))
            print(f"/n This is the server file {server_file}\n")
            print(f"/n this is params {params}")
            print(f"/n This is the question file {question_html}\n")
            solution_html = read_file(os.path.join(tmpdir, "solution.html"))
            question_html_template, solution_html_template = process_prairielearn_html(
                question_html,solution_html= solution_html, qdata=params, qname=quiz_name
            )
            print(question_html)
            return render_template(
                "question_base.html", 
                quiz_name=quiz_name, 
                question_html=question_html_template
            )
    except Exception as e:
        # Log the error with traceback for debugging purposes
        error_message = f"An error occurred while rendering the adaptive quiz: {str(e)}"
        traceback.print_exc()

        # Optionally, you can flash an error message to the user
        flash("An error occurred while generating the quiz. Please try again later.", "error")
        
        # Redirect to an error page or the previous page
        return "Error"



