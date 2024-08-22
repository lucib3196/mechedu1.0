# Standard Library Imports
import os
import tempfile
from ast import literal_eval

# Third-Party Imports
from flask import Blueprint, Flask, render_template, session, redirect, url_for, jsonify, flash

# Local Application Imports
from ...db_models.models import File, EduModule, Folder
from src.run_quizzes.run_module import generateAdaptive, run_generate_py, run_generate, read_file
from src.utils.plutilities import process_prairielearn_html

# Define Blueprint
module_retrieval_bp = Blueprint('module_retrieval_bp', __name__)

@module_retrieval_bp.route("/retrieve_modules", methods=['GET', 'POST'])
def view_modules():
    """Gets the modules from the database and returns the module data which is just the name 
    and the id for now

    Returns:
        renders the template
    """
    modules = EduModule.query.all()
    module_data = []
    for module in modules:
        module_data.append({
            'id': module.id,
            'name': module.name,
        })
    print(f"This is the module data {module_data}")
    return render_template("view_modules.html", modules=module_data)

@module_retrieval_bp.route("/retrieve_modules/<module_name>_<module_id>", methods=['GET', 'POST'])
def view_module_details(module_name,module_id):
    module = EduModule.query.filter_by(id=module_id).first()
    folder_data = []
    for folder in module.folders:
        folder_data.append({
            'id': folder.id,
            'folder_name': folder.name,
        })
    print(f"This is the folder data {folder_data}")
    session["folder_data"] = folder_data
    return render_template("module_content.html",folder_data=folder_data)




