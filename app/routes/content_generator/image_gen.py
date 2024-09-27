# Standard Library Imports
import asyncio
import os
import tempfile

# Third-Party Imports
from flask import Blueprint, render_template, session, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename

# Local Application Imports
from ...form.forms import ImageForm
from src.llm_content_assembly.assembly import generate_from_image
from .utils import save_generated_content
from src.logging_config.logging_config import get_logger

# Initialize the logger
logger = get_logger(__name__)

# User data to be used in the module generation
user_data = {
    "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
    "code_language": "javascript",
}

image_generator_bp = Blueprint('image_generator_bp', __name__)

@image_generator_bp.route("/image-generator", methods=['GET', 'POST'])
def generate_image():
    """
    Route for generating image-based modules from uploaded files.

    Renders a form for the user to upload images. Upon form submission, the images
    are processed asynchronously to generate modules. The generated content is then saved.

    Returns:
        Response: A Flask response object with either the generated content or an error message.
    """
    form = ImageForm()
    logger.info("Image form initialized.")
    
    if form.validate_on_submit():
        logger.info("Form passed validation.")
        session["module_name"] = form.module_name.data
        try:
            file_paths = []
            with tempfile.TemporaryDirectory() as tmpdir:
                logger.info("Saving uploaded files to temporary directory.")

                # Save uploaded files to the temporary directory
                for file in form.files.data:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(tmpdir, filename)
                    file.save(file_path)
                    file_paths.append(file_path)
                
                logger.info(f"Files saved to temporary directory: {file_paths}")

                # Use asyncio to run the generate function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Ensure this function is truly async-compatible with Flask
                generated_content, tokens = loop.run_until_complete(
                    generate_from_image(paths=file_paths, user_data=user_data)
                )
                loop.close()

                logger.info(f"Image-based content generation completed. Tokens used: {tokens}")

                # Call the function to save the generated content
                save_response, status_code = save_generated_content(generated_content,module_name=session['module_name'])
                if status_code != 200:
                    logger.error(f"Failed to save generated content. Status code: {status_code}")
                    return jsonify(save_response), status_code

            flash("Generation Successful!")
            logger.info("Content saved successfully and user notified.")
            return redirect(url_for('image_generator_bp.generate_image'))  # Corrected the redirect URL

        except Exception as e:
            logger.exception("An error occurred during the image generation process.")
            return jsonify({"error": "An error occurred while processing your request."}), 500
    
    return render_template("generate_from_image.html", form=form, files=session.get("files", ""))
