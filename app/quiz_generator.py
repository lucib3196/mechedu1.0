from flask import Blueprint, render_template,request,send_file
from run_generators import save_files_to_temp,create_zip_file,main
import os
import tempfile
import asyncio

quiz_generator = Blueprint('quiz_generator', __name__)
@quiz_generator.route('/generate_from_text', methods=['GET', 'POST'])

def generate_from_text():
    if request.method == "POST":
        text = request.form.get("user_question")
        if text:
            try:
                print("There is text!", text)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                generated_content, question_title = loop.run_until_complete(main(user_input=text))
                print("This is the generated_content", generated_content)
                print("/n")
                loop.close()
                
                with tempfile.TemporaryDirectory() as tmpdirname:
                    folder_path = os.path.join(tmpdirname, question_title)
                    os.makedirs(folder_path, exist_ok=True)
                    file_paths = save_files_to_temp(generated_content, folder_path)
                    zip_file = create_zip_file(file_paths, tmpdirname)
                    print("Process complete")
                    return send_file(zip_file, mimetype='application/zip', as_attachment=True, download_name='module.zip')
            except Exception as e:
                print(f"An error occurred: {e}")
                return "An error occurred while processing your request.", 500
        else:
            return "No text provided", 400
    else:
        return "Please submit a POST request.", 405
    
@quiz_generator.route('/generate_from_image', methods=['GET', 'POST'])
def generate_from_image():
    if request.method == "POST":
        files = request.files.getlist('user_images')
        if not files or all(file.filename == '' for file in files):
            return 'No Selected File', 400
        
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
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            generated_content, question_title = loop.run_until_complete(main(user_input=temp_file_paths))
            loop.close()
            
            with tempfile.TemporaryDirectory() as tmpdirname:
                folder_path = os.path.join(tmpdirname, question_title)
                os.makedirs(folder_path, exist_ok=True)
                file_paths = save_files_to_temp(generated_content, folder_path)
                zip_file = create_zip_file(file_paths, tmpdirname)
                print("Process complete")
                return send_file(zip_file, mimetype='application/zip', as_attachment=True, download_name='module.zip')
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return 'Image processing failed', 500

        finally:
            for path in temp_file_paths:
                if os.path.exists(path):
                    os.remove(path)

    return 'Invalid request method', 405
