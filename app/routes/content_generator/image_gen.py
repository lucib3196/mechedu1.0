# Standard Library Imports
import asyncio
import os
from flask import request

# Third-Party Imports
from flask import Blueprint, Flask, render_template, session, redirect, url_for, jsonify, flash
import tempfile
from werkzeug.utils import secure_filename

# Local Application Imports
from ...form.forms import ImageForm
from src.gestalt_module_generator.generate_gestalt_module import generate_module
from .utils import save_generated_content

user_data = {
        "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
        "code_language": "javascript",
    }


image_generator_bp = Blueprint('image_generator_bp', __name__)
@image_generator_bp.route("/image-generator", methods=['GET', 'POST'])
def generate_image():

    form = ImageForm()
    print(form)
    if form.validate_on_submit():
        print("Passed validation")
        try:
            file_paths = []
            with tempfile.TemporaryDirectory() as tmpdir:
                print("About to save files")
                
                # Save uploaded files to the temporary directory
                for file in form.files.data:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(tmpdir, filename)
                    file.save(file_path)
                    file_paths.append(file_path)
                
                print(f"Saved file paths to temp: {file_paths}")

                # Use asyncio to run the generate function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Ensure this function is truly async-compatible with Flask
                generated_content = loop.run_until_complete(generate_module(user_input=file_paths, user_data=user_data))
                loop.close()

                # Call the function to save the generated content
                save_response, status_code = save_generated_content(generated_content)
                if status_code != 200:
                    return jsonify(save_response), status_code

            flash("Generation Successful!!!!")
            return redirect(url_for('image_generator_bp.generate_image'))  # Corrected the redirect URL

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"error": "An error occurred while processing your request."}), 500
    
    return render_template("generate_from_image.html", form=form, files=session.get("files", ""))