import os
import json
import importlib.util
import sys
from src.prairielearn.python import prairielearn as pl

# Define the path to the elements directory
path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\prairielearn\elements"

# Get the absolute path to the 'src' directory relative to the current working directory
current_working_directory = os.getcwd()
src_dir = os.path.join(current_working_directory, 'src')

# Add the 'src' directory to sys.path so Python can find the modules
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# List of valid elements (controllers)
valid_elements = ["pl-answer-panel.py", "pl-number-input.py","pl-multiple-choice.py"]

# html_string = r"""
# <pl-multiple-choice answers-name="pressureSurfaceTensionRelation" weight="1" inline="true">
# """
# html_string = r"""
# <pl-multiple-choice answers-name="acc" weight="1">
#   <pl-answer correct="false">positive</pl-answer>
#   <pl-answer correct="true">negative</pl-answer>
#   <pl-answer correct="false">zero</pl-answer>
# </pl-multiple-choice>"""
html_string = r"""<pl-number-input answers-name="ans_rtol" label="$x =$"> </pl-number-input>"""
data: pl.QuestionData = {
    "params": {"test": 5},
    "correct_answers": {"ans_rtol": 5},
    "submitted_answers": {"ans_rtol":5},  # Make sure the key matches the input name
    "format_errors": {},
    "partial_scores": {},
    "score": 100,
    "feedback": {"comment": "Great job"},
    "variant_seed": "seed123",
    "options": {},
    "raw_submitted_answers": {"answer1": "10"},
    "editable": True,
    "panel": "question",
    "extensions": {},
    "num_valid_submissions": 3,  # Important
    "manual_grading": False,  # Important
    "answers_names": {"answer1": True},
}

# Walk through the directory structure
for root, dirs, files in os.walk(path):
    for file in files:
        # Look for the info.json file
        if file == "info.json":
            info_json_path = os.path.join(root, file)
            
            # Open and load the info.json file
            try:
                with open(info_json_path, 'r') as f:
                    contents_dict = json.load(f)  # Load JSON content
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading {info_json_path}: {e}")
                continue

            # Get the controller file from the JSON
            controller = contents_dict.get("controller")
            
            # Check if the controller is in the list of valid elements
            if controller in valid_elements:
                controller_path = os.path.join(root, controller)
                
                if os.path.exists(controller_path):
                    # Dynamically import the controller module
                    module_name = os.path.splitext(controller)[0]  # Remove the file extension for the module name
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, controller_path)
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[module_name] = module
                        spec.loader.exec_module(module)
                        if hasattr(module, 'render') and hasattr(module, 'prepare'):
                            module.prepare(html_string,data)
                            output_html = module.render(html_string,data)
                            print(f"This is the output format {output_html}")
                        
                        # Print the dependencies from the info.json file
                        dependencies = contents_dict.get("dependencies", {})
                        print(f"Dependencies for {controller}: {dependencies}")
                    
                    except Exception as e:
                        print(f"Error loading module {controller}: {e}")
                else:
                    print(f"Controller file not found: {controller_path}")


