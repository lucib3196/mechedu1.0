import importlib.util
import execjs
import os
import json
from ..utils.plutilities import process_prairielearn_html
def import_module_from_path(path):
    """imports a module and returs a module

    Args:
        path (str): path to module

    Returns:
        <class 'module'>: returns a module that i can run. 
    """
    # The function of interest is generate
    spec = importlib.util.spec_from_file_location("generate",path)
    # Load the module from the created spec
    module = importlib.util.module_from_spec(spec)  
    # Execute the moduel to make attribute accessible
    spec.loader.exec_module(module)
    # Return the imported module
    return module

def run_generate_py(path:str)->dict:
    """Imports a server.py module from a path, then we run the function generate found inside the function 

    Args:
        path (str): path to the module

    Returns:
        dict: A dictionary containing params for question 
    """
    module = import_module_from_path(path)
    data = module.generate()
    return data

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
def file_exist(file_path:str)->bool:
    return os.path.exists(file_path)
    
def read_file(file_path:str):
    file_exist(file_path)
    with open(file_path,"r") as file:
        return file.read()
    
def generateAdaptive(quiz_path:str,code_lang:str="python"):
    files_to_check = ["question.html", "server.js","server.py","info.json","solutions.html"]
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
        print(f"Found params {params}\n")
        print(f'This is the type {type(params)}')
        
    try:
        question_html = read_file(valid_files.get("question.html"))
        solution_html = read_file(valid_files.get("solutions.html"))
        question_html_template, solution_html_template = process_prairielearn_html(question_html,solution_html,qdata=params,qname=quiz_name)
        
    except FileNotFoundError:
        return "Quiz content template not found", 404
    return question_html_template, solution_html_template, params

# path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu\website\quizzes\01_physics1\AccelerationDownInclineWithFriction\server.py"
# path_js = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu\website\quizzes\01_physics1\AccelerationDownInclineWithFriction\server.js"
# print(run_generate_py(path))
# print(run_generate_js(path_js))