# Standard Library Imports
import asyncio

# Third-Party Imports
from flask import Blueprint, Flask, render_template, session, redirect, url_for, jsonify, flash

# Local Application Imports
from ...form.forms import QuestionForm
from src.gestalt_module_generator.generate_gestalt_module import generate_module
from .utils import save_generated_content


text_generator_bp = Blueprint("text_generator_bp", __name__)
# Should be changed later on to get user information
user_data = {
        "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
        "code_language": "javascript",
    }

@text_generator_bp.route("/text-generator", methods=['GET', 'POST'])
def generate_text():
    form = QuestionForm()
    if form.validate_on_submit():
        session["question"] = form.question.data
        try:
            print(f"This is the user question to be generated: {session['question']}")

            # Create an event loop to run the function asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            generated_content = loop.run_until_complete(
                generate_module(user_input=session["question"], user_data=user_data)
            )
            loop.close()

            # Call the function to save the generated content
            save_response, status_code = save_generated_content(generated_content)
            if status_code != 200:
                return jsonify(save_response), status_code
            
            flash("Generation Successful!!!!")
            return redirect(url_for('text_generator_bp.generate_text'))

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": "An error occurred while processing your request."}), 500

    return render_template("generate_from_text.html", form=form, question=session.get("question", ""))


