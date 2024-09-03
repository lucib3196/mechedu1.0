# Standard Library Imports
import asyncio

# Third-Party Imports
from flask import Blueprint, Flask, render_template, session, redirect, url_for, jsonify, flash

# Local Application Imports
from ...form.forms import QuestionForm
from .utils import save_generated_content
from src.llm_content_assembly.assembly import generate_module_text
from src.logging_config.logging_config import get_logger

# Initialize the logger
logger = get_logger(__name__)

# Create the Blueprint
text_generator_bp = Blueprint("text_generator_bp", __name__)

# User data to be used in the module generation
user_data = {
    "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
    "code_language": "javascript",
}

@text_generator_bp.route("/text-generator", methods=['GET', 'POST'])
def generate_text():
    """
    Route for generating text-based modules from user input.
    
    Renders a form for the user to input a question. Upon form submission, the question
    is processed asynchronously to generate a module. The generated content is then saved.
    
    Returns:
        Response: A Flask response object with either the generated content or an error message.
    """
    form = QuestionForm()

    if form.validate_on_submit():
        session["question"] = form.question.data
        logger.info(f"Received user question for generation: {session['question']}")

        try:
            # Create an event loop to run the function asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            generated_content, tokens = loop.run_until_complete(
                generate_module_text(question=session["question"], user_data=user_data)
            )
            loop.close()

            logger.info(f"Text generation completed. Tokens used: {tokens}")

            # Call the function to save the generated content
            save_response, status_code = save_generated_content(generated_content)
            if status_code != 200:
                logger.error(f"Failed to save generated content. Status code: {status_code}")
                return jsonify(save_response), status_code

            flash("Generation Successful!")
            logger.info("Content saved successfully and user notified.")
            return redirect(url_for('text_generator_bp.generate_text'))

        except Exception as e:
            logger.exception("An error occurred during the text generation process.")
            return jsonify({"error": "An error occurred while processing your request."}), 500

    return render_template("generate_from_text.html", form=form, question=session.get("question", ""))
