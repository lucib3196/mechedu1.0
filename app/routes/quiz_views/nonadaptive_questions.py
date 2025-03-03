# Standard Library Imports
import os
import tempfile
import traceback
import logging

# Third-Party Imports
from flask import Blueprint, render_template, session, redirect, url_for, flash

# Local Application Imports
from src.run_quizzes.run_module import generateAdaptive, run_generate_py, run_generate, read_file
from src.utils.plutilities import process_prairielearn_html
from ...db_models.models import Folder
from .utils import retrieve_files_folder
from src.process_prairielearn.process_prairielearn import format_question_html
from src.prairielearn.python import prairielearn as pl
from src.logging_config.logging_config import get_logger

# Blueprint Definition
non_adaptive_quiz_bp = Blueprint('non_adaptive_quiz_bp', __name__)

# Initialize logger
logger = get_logger(__name__)

@non_adaptive_quiz_bp.route("/quiz_overview/non_adaptive", methods=['GET', 'POST'])
def render_non_adaptive_quiz():
    try:
        # Retrieve folder information from session
        folder_id = session.get("folder_id")
        if not folder_id:
            return "Folder ID not found in session", 400

        folder_name, full_files_data = retrieve_files_folder(folder_id)

        # Create a temporary directory to handle file processing
        with tempfile.TemporaryDirectory() as tmpdir:
            for file in full_files_data:
                filename = file.get("filename")
                content = file.get("content", "")

                # Convert content to bytes if it's a string
                if isinstance(content, str):
                    content = content.encode('utf-8')

                # Write content to a temporary file
                tempfile_path = os.path.join(tmpdir, filename)
                with open(tempfile_path, "wb") as f:
                    f.write(content)
                
                logger.info(f"Temporary file created at: {tempfile_path}")

            # Generate quiz data
            # server_file = os.path.join(tmpdir, "server.js")
            # generated_data = run_generate(server_file)
            # params = generated_data.get("params", {})
            # correct_answers = generated_data.get("correct_answers", {})

            # Load question and solution HTML
            question_html = read_file(os.path.join(tmpdir, "question.html"))
            # solution_html = read_file(os.path.join(tmpdir, "solution.html"))
            print(question_html)
            # Populate the question data
            data: pl.QuestionData = {
                "params": {},
                "correct_answers": {},
                "submitted_answers": {},  # Empty initially
                "format_errors": {},
                "partial_scores": {},
                "score": 0,
                "feedback": {"comment": "Great job"},  # Feedback placeholder
                "variant_seed": "seed123",  # Random seed
                "options": {},
                "raw_submitted_answers": {},
                "editable": True,  # Marks whether the question is editable
                "panel": "question",  # Initial panel for displaying the question
                "extensions": {},
                "num_valid_submissions": 3,  # Number of valid submissions allowed
                "manual_grading": False,  # No manual grading needed
                "answers_names": {}
            }
            session["data"] = data

            # Format and log the question HTML
            formatted_question_html = format_question_html(question_html, data=data)
            logger.debug(f"Formatted Question HTML: {formatted_question_html}")

            # Store formatted question HTML in session
            session["question_html"] = question_html

            # Render the template with the formatted question
            return render_template(
                "question_base.html",
                quiz_name=folder_name,
                question_html=formatted_question_html
            )

    except Exception as e:
        logger.error(f"Error in rendering adaptive quiz: {str(e)}")
        return "An error occurred while rendering the quiz", 500