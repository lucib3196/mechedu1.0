from ...db_models.models import db, EduModule, Folder,File, QuestionMetadata
import tempfile
import os
import json
import uuid

def save_generated_content(generated_content, module_name:str = "Module"):
    """
    Save the generated content to the database, including the module, folders, and files.

    This function processes the generated content by:
    1. Creating and saving an `EduModule` instance.
    2. Iterating over the generated content to create and save corresponding `Folder` and `File` instances.
    3. Temporarily storing files in a directory before saving their binary contents to the database.

    Args:
        generated_content (list of tuples): The content generated by the module, where each tuple contains:
            - question_title (str): The title of the question (used as the folder name).
            - module_content (dict): A dictionary where keys are file names and values are file contents.
        module_name (str): The name of the module to be saved in the database. Defaults to "Module".

    Returns:
        tuple: A dictionary containing a success message or error message, and the corresponding HTTP status code.
    """
    try:
        # Create and save the EduModule instance
        module = EduModule(name=module_name)
        db.session.add(module)
        db.session.flush()  # Ensure module.id is available for use in Folder instances

        # Iterate over the generated content
        for result in generated_content:
            if isinstance(result,list):
                result = result[0]
            question_title, module_content = result
            print(f"This is the question: {question_title}\nThis is the module content: {module_content}")

            # Create and save the Folder instance associated with the module
            folder = Folder(name=question_title, module_id=module.id)
            db.session.add(folder)
            db.session.flush()  # Ensure folder.id is available for use in File instances
            # Create a temporary directory to store the files
            with tempfile.TemporaryDirectory() as tmpdir:
                if not tmpdir:
                    return {"error": "Failed to create temporary directory."}, 500

                print(f"Temporary directory path: {tmpdir}")

                # Iterate over the module content to save each file
                for file_name, file_contents in module_content.items():
                    print(f"This is the file name: {file_name}\nContents:\n{file_contents}\n{'*'*50}\n")
                    file_path = os.path.join(tmpdir, file_name)


                    # Convert file_contents to JSON string if it is a dictionary
                    if isinstance(file_contents, dict):
                        file_contents = json.dumps(file_contents, indent=4)

                    if file_name == "info.json":

                        if isinstance(file_contents,str):
                            try:
                                file_contents = json.loads(file_contents)
                            except json.JSONDecodeError as e:
                                print(f"Failed to parse info.json: {e}")
                                continue

                            # Assuming file_contents is already a dictionary parsed from the JSON file
                            question_metadata = QuestionMetadata(
                                uuid=str(uuid.uuid4()),
                                title=file_contents.get("title"),
                                stem=file_contents.get("stem"),
                                topic=file_contents.get("topic"),
                                tags=json.dumps(file_contents.get("tags", [])),  # Assuming tags is a list
                                prereqs=json.dumps(file_contents.get("prereqs", [])),  # Assuming prereqs is a list
                                is_adaptive=file_contents.get("isAdaptive", False),  # Convert key to snake_case
                                created_by=file_contents.get("createdBy", "unknown"),  # Convert key to snake_case
                                q_type=file_contents.get("qType", "unknown"),  # Convert key to snake_case
                                n_steps=file_contents.get("nSteps", 1),  # Convert key to snake_case
                                updated_by=file_contents.get("updatedBy", ""),  # Convert key to snake_case
                                difficulty=file_contents.get("difficulty", 1),
                                codelang=file_contents.get("codelang", "javascript"),
                                reviewed=file_contents.get("reviewed", False),
                                folder_id=folder.id  # Assuming folder.id is defined elsewhere in your code
                            )
                            db.session.add(question_metadata)

                    # Ensure file_contents is in binary format for storage
                    if isinstance(file_contents, str):
                        file_contents = file_contents.encode('utf-8')
                    elif isinstance(file_contents, dict):
                        # Convert dict to JSON string, then to bytes
                        file_contents = json.dumps(file_contents, indent=4).encode('utf-8')

                    # Write the file contents to the temporary directory
                    with open(file_path, "wb") as file:
                        file.write(file_contents)


                    # Create and save the File instance associated with the folder
                    file_record = File(filename=file_name, content=file_contents, folder_id=folder.id)
                    db.session.add(file_record)

        # Commit all changes to the database
        db.session.commit()
        return {"message": "Files stored in the database successfully."}, 200

    except Exception as e:
        # Rollback the session in case of an error
        db.session.rollback()
        print(f"An error occurred: {e}")
        return {"error": str(e)}, 500
