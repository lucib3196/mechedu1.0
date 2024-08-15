from flask import Blueprint,render_template,request,send_file,jsonify,session
import os
import tempfile
import asyncio
import json

from src.gestalt_module_generator.generate_gestalt_module import generate
from src.utils.file_handler import save_files_temp,save_temp_dir_as_zip


quiz_generator = Blueprint('quiz_generator', __name__)
@quiz_generator.route('/generate_from_text', methods=['POST'])
def generate_from_text():
    text = request.form.get("user_question")
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        print(f"This is the user question to be generated: {text}")

        # Use asyncio to run the generate function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        generated_content = loop.run_until_complete(generate(user_input=text))
        loop.close()

        # Extract and handle the metadata from the generated content
        metadata = generated_content.get("info.json", {})

        if isinstance(metadata, dict):
            print(f"Metadata: {metadata}")
            title = metadata.get("title")
            print(f"Title: {title}")
        else:
            print("Expected metadata to be a dictionary, but got something else.")
            metadata = {}

        # Save the files to a temporary directory and get the path
        question_title = metadata.get("title", "default_title")
        temp_dir = generate_temp(question_title=question_title, generated_content=generated_content)

        if not temp_dir:
            return jsonify({"error": "Failed to create temporary directory."}), 500

        print(f"Temporary directory path: {temp_dir}")
        return render_template("home.html")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

@quiz_generator.route('/generate_from_image', methods=['POST'])
def generate_from_image():
    files = request.files.getlist('user_images')
    
    if not files:
        return jsonify({"error": "No files provided"}), 400
    
    temp_file_paths = []
    try:
        for file in files:
                if file and file.filename:
                    temp_file = tempfile.NamedTemporaryFile(delete=False)
                    file.save(temp_file.name)
                    temp_file_path = os.path.abspath(temp_file.name)
                    temp_file.close()
                    temp_file_paths.append(temp_file_path)
                    print("Temp file path:", temp_file_path)
        print("Temp file paths:", temp_file_paths)
        

        # Use asyncio to run the generate function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        generated_contents = loop.run_until_complete(generate(user_input=temp_file_paths))
        loop.close()
        print(f"{'*'*25}\n {generated_contents}\n{'*'*25}")
        for generated_content in generated_contents:
            # Extract and handle the metadata from the generated content
            metadata = generated_content.get("info.json", {})

            if isinstance(metadata, dict):
                print(f"Metadata: {metadata}")
                title = metadata.get("title")
                print(f"Title: {title}")
            else:
                print("Expected metadata to be a dictionary, but got something else.")
                metadata = {}

            # Save the files to a temporary directory and get the path
            question_title = metadata.get("title", "default_title")
            temp_dir = generate_temp(question_title=question_title, generated_content=generated_content)

            if not temp_dir:
                return jsonify({"error": "Failed to create temporary directory."}), 500

            print(f"Temporary directory path: {temp_dir}")
        return render_template("home.html")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


@quiz_generator.route('/download_zip', methods=['GET','POST'])
def download_zip():
    temp_dir = session.get("temp_dir","")
    print(temp_dir)
    zip_file = save_temp_dir_as_zip(temp_dir)
    return send_file(zip_file, mimetype='application/zip', as_attachment=True, download_name='module.zip')


def generate_temp(question_title, generated_content):
    # Generate the temporary directory
    temp_dir = save_files_temp(question_title, generated_content)
    
    # Store the path in the session
    session['temp_dir'] = temp_dir
    print(temp_dir)
    
    return f"Temporary directory generated and stored in session."