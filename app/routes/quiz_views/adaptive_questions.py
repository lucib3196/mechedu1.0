# Standard Library Imports
from operator import sub
import os
import tempfile
import traceback
import logging
from flask import request
import json

# Third-Party Imports
from flask import Blueprint, render_template, session, redirect, url_for, flash

# Local Application Imports
from src.run_quizzes.run_module import generateAdaptive, run_generate_py, run_generate, read_file
from src.utils.plutilities import process_prairielearn_html
from ...db_models.models import Folder
from .utils import retrieve_files_folder
from src.process_prairielearn.process_prairielearn import format_question_html,format_solution_html
from src.prairielearn.python import prairielearn as pl
from src.logging_config.logging_config import get_logger
from flask_wtf.csrf import generate_csrf
# Blueprint Definition
adaptive_quiz_bp = Blueprint('adaptive_quiz_bp', __name__)

# Initialize logger
logger = get_logger(__name__)

@adaptive_quiz_bp.route("/quiz_overview/_adaptive", methods=['GET', 'POST'])
def render_adaptive_quiz():
    csrf_token = generate_csrf()
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
                print(content)

                # Convert content to bytes if it's a string
                if isinstance(content, str):
                    content = content.encode('utf-8')
                if isinstance(content,dict):
                    content = json.dumps(content).encode('utf-8')

                # Write content to a temporary file
                tempfile_path = os.path.join(tmpdir, filename)
                with open(tempfile_path, "wb") as f:
                    f.write(content)
                    print(content)
                
                logger.info(f"Temporary file created at: {tempfile_path}")

            # Generate quiz data
            server_file = os.path.join(tmpdir, "server.js")
            generated_data = run_generate(server_file)
            print(generated_data)
            params = generated_data.get("params", {})
            correct_answers = generated_data.get("correct_answers", {})

            # Load question and solution HTML
            question_html = read_file(os.path.join(tmpdir, "question.html"))
            solution_html = read_file(os.path.join(tmpdir, "solution_flask.html"))

            # Populate the question data
            data: pl.QuestionData = {
                "params": params,
                "correct_answers": correct_answers,
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
            logger.info(f"Formatted Question HTML: {formatted_question_html}")
            
            print(solution_html)
            solution_html =  format_solution_html(html_content = solution_html,data=data)
            logger.info(f"Formatted Question HTML: {solution_html}")

            # Store formatted question HTML in session
            session["question_html"] = question_html

            # Render the template with the formatted question
            return render_template(
                "question_base.html",
                quiz_name=folder_name,
                question_html=formatted_question_html,csrf_token=csrf_token,solution_html =solution_html)

    except Exception as e:
        logger.error(f"Error in rendering adaptive quiz: {e}")
        # if 'str' in str(e):
        #     raise TypeError(f"Error in rendering adaptive quiz:  is a string and cannot be called as a function. "
        #                     "Please check if you're overwriting a function with a string or using the wrong variable type. "
        #                     f"Occurred at line 101 in adaptive_questions.py")
        return "An error occurred while rendering the quiz", 500
    

@adaptive_quiz_bp.route("/quiz_overview/_adaptive/grade", methods=['GET', 'POST'])
def grade_quiz():
    print("Grading")
    try:
        # Retrieve folder information from session
        folder_id = session.get("folder_id")
        if not folder_id:
            return "Folder ID not found in session", 400

        folder_name, full_files_data = retrieve_files_folder(folder_id)
        quiz_name = folder_name

        # Process form submission
        if request.method == 'POST':
            form_data = request.form.to_dict()
            logger.info(f"Form Data: {form_data}")
            print(form_data.items())

            submitted_answers = {}
            for field,value in form_data.items():
                submitted_answers[field] = value
            # Store submitted answers
            print(submitted_answers)
            logger.debug(f"Submitted Answers: {submitted_answers}")

            # Retrieve question data from session
            data = session.get("data")
            if not data:
                return "No quiz data found in session", 400
            print(data)
            # Update data with submitted answers and panel information
            data["submitted_answers"] = submitted_answers
            data["panel"] = "answer"

            print(type(data))

            # Retrieve question HTML and format it
            question_html = session.get("question_html")
            if not question_html:
                return "Question HTML not found in session", 400

            formatted_question_html = format_question_html(question_html, data=data)
            logger.debug(f"Formatted Question HTML: {formatted_question_html}")
            print(formatted_question_html)
            # Render the template with the updated question
            return render_template(
                "question_base.html",
                quiz_name=quiz_name,
                question_html=formatted_question_html
            )

        else:
            # Handle non-POST requests
            return "Invalid method. Please submit the form.", 405

    except Exception as e:
        logger.error(f"Error while grading quiz: {str(e)}")
        return "An error occurred while grading the quiz", 500




