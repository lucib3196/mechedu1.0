import importlib.util
import os
import json
import execjs 
from src.utils.plutilities import process_prairielearn_html
def file_exist(file_path:str)->bool:
    return os.path.exists(file_path)
    
def read_file(file_path:str):
    file_exist(file_path)
    with open(file_path,"r") as file:
        return file.read()
    
    
def import_module_from_path(path:str):
    # We are looking for the generate module in the python file
    spec = importlib.util.spec_from_file_location("generate",path)
    # Load the module
    module = importlib.util.module_from_spec(spec)  
    # Execute the moduel to make attribute accessible
    spec.loader.exec_module(module)
    # Return the imported module
    return module

def run_generate_py(path_server_py:str):
    """Run the server.py module

    Args:
        path_server_py (str): path to server.py file

    Returns:
        module.generate(): Should be a dictionary containing valus, not sure need to check
    """
    module = import_module_from_path(path_server_py)
    return module.generate()

def run_generate_js(path):
    with open(path, 'r') as file:
        js_code = file.read()
    context = execjs.compile(js_code)
    return context.call("generate")

def run_generate(path:str):
    generators = {
        "server.js": run_generate_js,
        "server.py": run_generate_py
    }
    if not os.path.isfile(path):
        return ({"error": "File not found"}), 404
    
    base_name = os.path.basename(path)
    try:
        if base_name in generators.keys():
            func = generators[base_name]
            data =func(path)
            return data
    except Exception as e:
        return {"error": str(e)}, 400
    return base_name


def generateAdaptive(quiz_path:str,code_lang:str="python"):
    files_to_check = ["question.html", "server.js","server.py","info.json","solution.html"]
    valid_files = {file:os.path.join(quiz_path, file) for file in files_to_check if file_exist(os.path.join(quiz_path, file))}
    print(valid_files)
    quiz_name = os.path.basename(quiz_path)
    server_file = None
    if code_lang.lower()=="python":
        server_file = valid_files.get("server.py")
    elif code_lang.lower() == "javascript":
        server_file = valid_files.get("server.js")
    
    if server_file:
        params = run_generate(server_file)
        print(params)
        
    print("*"*25)
    print(valid_files)
    try:
        
        question_html = read_file(valid_files.get("question.html"))
        solution_html = read_file(valid_files.get("solution.html"))
        question_html_template, solution_html_template = process_prairielearn_html(question_html,solution_html,qdata=params,qname=quiz_name)
        
    except FileNotFoundError:
        return "Quiz content template not found", 404
    return question_html_template, solution_html_template, params


# print(generateAdaptive(r"mechedu1.0\question"))