from flask import Blueprint,render_template,request,send_file,jsonify,session
import os
import tempfile
import asyncio
import json
from typing import Union
from flask import Blueprint, request, jsonify
import asyncio
import os
import tempfile
from .models import db, File, Folder
from src.gestalt_module_generator.generate_gestalt_module import generate_module
from src.utils.file_handler import save_files_temp,save_temp_dir_as_zip
import os
import json
import asyncio
import tempfile
from flask import request, jsonify
from werkzeug.utils import secure_filename

user_data = {
        "created_by": "lberm007@ucr.edu",  # Replace with the actual creator identifier
        "code_language": "javascript",
    }
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
        generated_content = loop.run_until_complete(generate_module(user_input=text, user_data=user_data))
        loop.close()

        for result in generated_content:
            question_title, module = result
            print(f"This is the question: {question_title}\nThis is the module content: {module}")

            # Create a Folder entry in the database using the question title
            folder = Folder(name=question_title)
            db.session.add(folder)
            db.session.flush()  # Ensure the folder is available for the files

            with tempfile.TemporaryDirectory() as tmpdir:
                if not tmpdir:
                    return jsonify({"error": "Failed to create temporary directory."}), 500
                print(f"Temporary directory path: {tmpdir}")

                for file_name, file_contents in module.items():
                    print(f"This is the file name: {file_name}\nContents:\n{file_contents}\n{'*'*50}\n")
                    file_path = os.path.join(tmpdir, file_name)

                    # Convert dictionary to JSON string if file_contents is a dict
                    if isinstance(file_contents, dict):
                        file_contents = json.dumps(file_contents, indent=4)

                    # Ensure file_contents is binary for storage
                    if isinstance(file_contents, str):
                        file_contents = file_contents.encode('utf-8')
                    
                    # Write the file contents to the temporary directory
                    with open(file_path, "wb") as file:
                        file.write(file_contents)
                    
                    # Store the file information in the database and associate with the folder
                    file_record = File(filename=file_name, content=file_contents, folder=folder)
                    db.session.add(file_record)

            db.session.commit()

        return jsonify({"message": "Files stored in the database successfully."})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


@quiz_generator.route('/generate_from_image', methods=['POST'])
def generate_from_image():
    files = request.files.getlist('user_images')
    
    if not files:
        return jsonify({"error": "No files provided"}), 400
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            file_paths = []
            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(tmpdir, filename)
                file.save(file_path)  # Save the file to the temporary directory
                file_paths.append(file_path)
            
            print(f"Saved file paths: {file_paths}")

            # Use asyncio to run the generate function
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            generated_content = loop.run_until_complete(generate_module(user_input=file_paths, user_data=user_data))
            loop.close()

            for result in generated_content:
                question_title, module = result
                print(f"This is the question: {question_title}\nThis is the module content: {module}")

                # Create a Folder entry in the database using the question title
                folder = Folder(name=question_title)
                db.session.add(folder)
                db.session.flush()  # Ensure the folder is available for the files

                for file_name, file_contents in module.items():
                    print(f"This is the file name: {file_name}\nContents:\n{file_contents}\n{'*'*50}\n")
                    
                    # Convert dictionary to JSON string if file_contents is a dict
                    if isinstance(file_contents, dict):
                        file_contents = json.dumps(file_contents, indent=4)

                    # Ensure file_contents is binary for storage
                    if isinstance(file_contents, str):
                        file_contents = file_contents.encode('utf-8')
                    
                    # Store the file information in the database and associate with the folder
                    file_record = File(filename=file_name, content=file_contents, folder=folder)
                    db.session.add(file_record)

                db.session.commit()

        return jsonify({"message": "Files stored in the database successfully."})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500



@quiz_generator.route('/download_zip', methods=['GET','POST'])
def download_zip():
    temp_dirs = session.get("temp_dir","")
    print("These are teh temp dirs:,",temp_dirs)
    print("Going to download \n")
    for temp_dir in temp_dirs:
        zip_file = save_temp_dir_as_zip(temp_dir)
        return send_file(zip_file, mimetype='application/zip', as_attachment=True, download_name='module.zip')
    return jsonify(temp_dirs)



