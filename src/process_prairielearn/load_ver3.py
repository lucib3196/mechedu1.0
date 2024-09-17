from email.mime import base
import html
import os
import sys
import json
import importlib.util
import types
import re
import lxml
from lxml import etree
import lxml.html

# Local module imports
from ..logging_config.logging_config import get_logger
from ..prairielearn.python import prairielearn as pl
import numpy as np
import sympy
from jinja2 import Template

# Define valid elements
VALID_ELEMENTS: list[str] = [
    "pl-question-panel", "pl-number-input", "pl-checkbox", "pl-figure", 
    "pl-integer-input", "pl-matching", "pl-matrix-component-input", 
    "pl-matrix-input", "pl-multiple-choice", "pl-order-blocks", 
    "pl-symbolic-input", "pl-units-input","pl-matrix-latex","pl-card"
]

# Initialize logger
logger = get_logger(__name__)

# Helper Function used to escape Jinja 
## Not sure if this is the best way to do this 
def escape_jinja_in_latex(template: str) -> str:
    """
    Escapes Jinja2 curly braces within LaTeX math mode in an HTML template.

    Args:
        template (str): The HTML template string containing Jinja2 and LaTeX code.

    Returns:
        str: The modified template with Jinja2 expressions properly escaped within LaTeX math mode.
    """
    # Regex to find Jinja2 expressions within LaTeX math mode (\(...\) or \[...\])
    pattern = r'\\\((.*?)\\\)|\\\[(.*?)\\\]'
    
    def escape_curly_braces(match):
        # This function will escape {{ and }} inside LaTeX math mode
        content = match.group(0)
        content = re.sub(r'{{', r'{{{{', content)
        content = re.sub(r'}}', r'}}}}', content)
        return content
    
    # Apply the escaping function to all matches in the template
    escaped_template = re.sub(pattern, escape_curly_braces, template, flags=re.DOTALL)
    
    return escaped_template

def extract_valid_elements_from_html(html: str, valid_elements: list[str]=VALID_ELEMENTS) -> dict[str, list]:
    """
    Extract valid HTML elements and their children from an HTML string based on a list of allowed tags.
    
    This function parses the given HTML string, checks if each element belongs to the list of valid elements,
    and extracts both the element and its children (if applicable). If valid child elements are found, 
    they are recursively extracted and removed from the parent before the parent is converted to a string.

    Args:
        html (str): The HTML string to process.
        valid_elements (list[str]): A list of valid HTML element tags to extract.

    Returns:
        dict[str, list]: A dictionary where each key is a valid tag and the value is a list of extracted HTML strings 
                         (or nested dictionaries for children) corresponding to that tag.
    """
    extracted_content: dict[str, list] = {}
    tree = lxml.html.fromstring(html)
    
    # Convert the tree into a list so that we can safely modify the tree during iteration
    elements = list(tree.iter())

    for element in elements:
        # Check if the current element is one of the valid elements
        if element.tag in valid_elements:
            print(element.tag)
            # Prepare a dictionary to collect child elements (if they exist)
            collection: dict[str, list] = {}

            # Iterate over the element's children to extract nested valid elements
            for child in list(element):
                if child.tag in valid_elements:
                    # Recursively extract valid elements from the child
                    child_html = etree.tostring(child).decode('utf-8', errors='ignore')
                    print(child_html)
                    new_dict = extract_valid_elements_from_html(child_html, valid_elements)
                    
                    # Remove the child after extraction
                    element.remove(child)
                    
                    # Merge the child dictionary into the collection
                    for key, value in new_dict.items():
                        if key in collection:
                            collection[key].extend(value)
                        else:
                            collection[key] = value
            
            # Convert the current element (without its already-extracted children) to string
            extracted_html = etree.tostring(element).decode('utf-8', errors='ignore')
            
            # Add the extracted element to the result
            if element.tag in extracted_content:
                extracted_content[element.tag].append(extracted_html)
            else:
                if collection:
                    extracted_content[element.tag] = [extracted_html, collection]
                else:
                    extracted_content[element.tag] = [extracted_html]
    print(extracted_content)
    return extracted_content




def gather_element_info(base_dir: str, valid_elements: list[str] = VALID_ELEMENTS) -> dict[str, dict]:
    """
    Gathers information about available elements from JSON files within the specified directory structure.

    This function traverses through a directory, checks for valid element directories, 
    and attempts to load a corresponding `info.json` file for each element. 
    The loaded JSON data is returned in a dictionary where the keys are the element names 
    and the values are the loaded JSON content, with the directory path added.

    Args:
        base_dir (str): The base directory path where the "elements" folder is located.
        valid_elements (list[str], optional): A list of valid element names. Defaults to VALID_ELEMENTS.

    Returns:
        dict[str, dict]: A dictionary mapping valid element names to their respective `info.json` contents 
                         (with an added "path" key for each).
    """
    available_elements_info: dict[str, dict] = {}
    
    # Construct the path to the elements directory
    elements_path = os.path.join(base_dir, 'src', 'prairielearn', 'elements')

    # Log the elements path for debugging
    logger.debug(f"Elements path: {elements_path}")

    # Walk through the elements directory
    for root, _, _ in os.walk(elements_path):
        element_name = os.path.basename(root)
        
        # Only process valid elements
        if element_name in valid_elements:
            try:
                # Load the info.json file
                info_path = os.path.join(root, "info.json")
                with open(info_path, 'r') as f:
                    contents_dict = json.load(f)
                    contents_dict["path"] = root
            except (json.JSONDecodeError, IOError) as e:
                # Log any errors encountered while reading the file
                logger.error(f"Error reading {os.path.join(root, 'info.json')}: {e}")
                continue
            
            # Add the loaded info to the dictionary
            available_elements_info[element_name] = contents_dict
    
    return available_elements_info

def find_elements_to_load(html: str,extracted_elements:dict,element_info: dict[str, dict[str,str]]) -> set[str]:
    """
    Determines which elements from the HTML should be loaded by comparing them 
    with available elements in the provided element information.

    The function extracts valid elements from the provided HTML, collects unique 
    element instances into a set, and compares them with the keys from `element_info`.
    It returns a set of element names that exist in both the HTML and the element information.

    Args:
        html (str): The HTML string from which elements are extracted.
        element_info (dict[str, dict]): A dictionary containing information about available elements.

    Returns:
        set[str]: A set of element names that are present in both the extracted HTML and the element information.
    """
    # This technically is not needed as valid elements is being passed by both, however it is useful if we ever
    # Decide to change certain things or remove others. Just a tool i guess lol

    # Extract elements from the HTML and create a set of unique instances
    
    set_elements = set(extracted_elements)

    # Check for any nested dictionaries and update the set with their keys
    for k, v in extracted_elements.items():
        for item in v:
            if isinstance(item, dict):
                if all(item_key not in set_elements for item_key in item.keys()):
                    set_elements.update(item.keys())
    
    # Find intersection between the extracted elements and the available element info keys
    element_call = set_elements & set(element_info.keys())
    return element_call

def load_module_from_path(module_name: str, file_path: str):
    """
    Dynamically loads a module from the specified file path and handles dependencies by 
    adding the package root to sys.path if not already present.
    
    Args:
        module_name (str): The name to assign to the loaded module.
        file_path (str): The full file path to the module.
    
    Returns:
        Module: The loaded module object.
    """
    # Get the root directory of the file (two levels up from the file path)
    package_root = os.path.abspath(os.path.join(os.path.dirname(file_path), '..', '..',".."))

    # Add package root to sys.path if not already present
    if package_root not in sys.path:
        sys.path.insert(0, package_root)

    # Create a module spec from the file path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load the module from {file_path}")

    # Create a module from the spec
    module = importlib.util.module_from_spec(spec)

    # Execute the module to load it
    spec.loader.exec_module(module) # type: ignore

    # Optionally, add the module to sys.modules to make it available globally
    sys.modules[module_name] = module
    
    return module

def load_controllers(element_info: dict[str, dict], elements_to_call: set[str]) -> dict[str, object]:
    """
    Loads the controller modules for the specified elements by dynamically loading the 
    modules based on the information provided in `element_info`.

    Args:
        element_info (dict[str, dict]): A dictionary containing element information, including paths and controllers.
        elements_to_call (set[str]): A set of element names to load their corresponding controllers.

    Returns:
        dict[str, object]: A dictionary mapping element names to their loaded controller modules.

    Logs:
        - Logs an info message when a module is successfully loaded.
        - Logs an error message if there is an issue loading a module.
    """
    controllers = {}

    for call in elements_to_call:
        try:
            info = element_info.get(call, {})
            controller = info.get("controller", "")  # type: ignore
            root = info.get("path", "")  # type: ignore

            if controller:
                module = load_module_from_path(os.path.basename(root), os.path.join(root, controller))
                controllers[call] = module
                logger.info(f"Module {call} loaded successfully.")
            else:
                logger.warning(f"No controller found for element {call}.")

        except Exception as e:
            logger.error(f"Failed to load module for element {call}: {e}")
    
    return controllers
def run_controller(module: types.ModuleType, function_name: str, *args, **kwargs):
    """
    Executes a function from the given module if it exists and is callable.

    :param module: The module containing the function.
    :param function_name: The name of the function to execute.
    :param *args: Positional arguments to pass to the function.
    :param **kwargs: Keyword arguments to pass to the function.
    :return: The result of the function execution, or None if the function doesn't exist or an error occurs.
    """
    try:
        # Check if the function exists in the module
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            
            # Check if the function is callable
            if callable(func):
                return func(*args, **kwargs)
            else:
                raise TypeError(f"{function_name} is not callable.")
        else:
            raise AttributeError(f"Function {function_name} not found in the module.{module}")
    
    except Exception as e:
        print(f"Error: {e}")
        return None
def process_extracted_elements(
    html_str: str, 
    filtering_elements: list[str], 
    data: 'pl.QuestionData', 
    controllers: dict, 
    custom_component: str = None
) -> str:
    """
    Process HTML string recursively, iterate through elements, apply controllers, 
    and replace valid elements with rendered content. Optionally wrap the rendered
    HTML in a custom component template.

    Args:
        html_str (str): The HTML string to process.
        filtering_elements (list[str]): List of element tags to filter.
        data (pl.QuestionData): Data object containing information like submitted answers.
        controllers (dict): Dictionary of controllers for handling elements.
        custom_component (str): Optional custom component wrapper for elements.
            Use `{content}` as a placeholder in the template for rendered HTML.

    Returns:
        str: The processed and modified HTML string.
    """
    # Parse the provided HTML string into an element tree
    tree = lxml.html.fromstring(html_str)
    processed_elements = set()

    def process_element(element):
        """Recursive function to process element and its valid children."""
        valid_children = [child for child in element if child.tag in filtering_elements]

        # Recursively process valid children first
        for child in valid_children:
            process_element(child)

        # Now process the parent element
        controller = controllers.get(element.tag, "")
        logger.debug(f"Running controller for element '{element.tag}': {controller}")
        print(f"Running controller for element '{element.tag}': {controller}")

        # Prepare and render the element
        element_html = etree.tostring(element, encoding='unicode')
        run_controller(controller, "prepare", element_html=element_html, data=data)
        rendered_html = run_controller(controller, "render", element_html=element_html, data=data)

        # Check if grading is needed and perform it
        if data.get("submitted_answers", {}):
            logger.info("Grading Question")
            logger.debug(f"Correct answers: {data.get('correct_answers')}")
            logger.debug(f"Submitted answers: {data.get('submitted_answers')}")
            run_controller(controller, "parse", element_html=element_html, data=data)
            run_controller(controller, "grade", element_html=element_html, data=data)

        # If valid rendered HTML is returned, wrap it in custom component or use raw rendered HTML
        if rendered_html and isinstance(rendered_html, str):
            # Wrap rendered HTML in custom component template if provided
            if custom_component:
                rendered_html = custom_component.format(content=rendered_html)

            parent = element.getparent()
            if parent is not None:
                index = parent.index(element)
                processed_elements.add(element)

                # Remove element and replace it with the rendered HTML
                parent.remove(element)
                if index == 0:
                    parent.text = (parent.text or "") + rendered_html
                else:
                    prev_sibling = parent[index - 1]
                    prev_sibling.tail = (prev_sibling.tail or "") + rendered_html
            else:
                logger.warning(f"The element {element.tag} has no parent to replace in.")
        else:
            logger.warning(f"Invalid rendered HTML for element {element.tag}: {rendered_html}")
    
    # Collect the elements to process after traversal
    elements_to_process = [e for e in tree.iter() if e.tag in filtering_elements and e not in processed_elements]

    # Process all collected elements
    for e in elements_to_process:
        process_element(e)

    # After processing, serialize the entire tree to a string
    try:
        modified_html = html.unescape(etree.tostring(tree, pretty_print=True).decode('utf-8'))
    except UnicodeDecodeError as e:
        raise ValueError(f"Decoding error while converting the tree to a string: {e}")

    return modified_html


def format_question_html(html: str, data: pl.QuestionData,isTesting:bool=False) -> str:
    """
    Formats a given question HTML by extracting relevant elements, loading controllers, and creating a 
    question panel and form area. The final output is a full HTML document with Bootstrap and MathJax support.

    Args:
        html (str): The HTML string representing the question structure.
        data (pl.QuestionData): The data associated with the question, including parameters and correct answers.

    Returns:
        str: A fully formatted HTML string containing the question panel and form area.
    """
    # Extract valid elements from the provided HTML
    extracted_elements = extract_valid_elements_from_html(html)

    # Load element info and gather the elements that need to be called
    current_directory = os.getcwd()
    element_info = gather_element_info(current_directory)
    elements_to_call = find_elements_to_load(html, extracted_elements, element_info)

    # Load the controllers for the elements
    controllers = load_controllers(element_info, elements_to_call)

    # Process the question panel elements
    question_panel_keys = ["pl-question-panel","pl-matrix-latex", "pl-figure", "pl-card"]
    filtered_question_panels = {panel_key: extracted_elements.pop(panel_key) 
                                for panel_key in question_panel_keys if panel_key in extracted_elements}

    # Generate HTML for the question panel using the controllers
    panel_html = process_extracted_elements(filtered_question_panels, controllers, data)

    # Process input elements (like number input, checkbox, etc.)
    input_panel_keys = [
        "pl-number-input", "pl-checkbox", "pl-integer-input", "pl-matching", "pl-matrix-component-input",
        "pl-matrix-input", "pl-multiple-choice", "pl-order-blocks", "pl-symbolic-input", "pl-units-input"
    ]
    filtered_input_panels = {panel_key: extracted_elements.pop(panel_key) 
                             for panel_key in input_panel_keys if panel_key in extracted_elements}

    custom_input = """
    <div class="card m-3">
        <div class="card-body">
            {content}
        </div>
    </div>"""

    # Generate HTML for the form area (inputs) using the controllers
    form_area = process_extracted_elements(filtered_input_panels, controllers, data, custom_component=custom_input)

    # Format the question panel in a Bootstrap card
    question_html = f"""
    <div class="card mb-3">
        <div class="card-header">
            Question
        </div>
        <div class="card-body">
            {panel_html}
        </div>
    </div>
    """

    # Improved form layout using Bootstrap form grid
    form_html = f"""
    <form method="post">
        <div class="row mb-3">
            <div class="col-12">
                {form_area}
            </div>
        </div>
        <div class="row">
            <div class="col-md-6">
                <button type="submit" class="btn btn-primary">Submit</button>
            </div>
            <div class="col-md-6">
                <button type="reset" class="btn btn-secondary">Reset</button>
            </div>
        </div>
    </form>
    """

    # Combine question panel and form into the final HTML
    question_html += form_html

    # Generate the full HTML document with Bootstrap and MathJax support
    full_html = f"""
    <div class="container my-5">
        {question_html}
    </div>
    """
    if isTesting:
        header = r"""
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <!-- Default CSS files -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
            <link rel="stylesheet" href="styles.css">  <!-- Corrected missing '=' sign -->
        </head>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
        <script type="text/javascript">
            window.MathJax = {
                tex: {
                    inlineMath: [['$', '$'], ['\\(', '\\)']],
                    displayMath: [['$$', '$$'], ['\\[', '\\]']]
                }
            };
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        """
        full_html = header+full_html


    # Extract params and render the template
    params = data.get("params", {})
    full_html = Template(escape_jinja_in_latex(full_html)).render(params=params)

    # Return the complete formatted HTML
    return full_html


def format_question_html2(html: str, data: pl.QuestionData,isTesting:bool=False) -> str:
    # Extract valid elements from the provided HTML
    extracted_elements = extract_valid_elements_from_html(html)
    # Load element info and gather the elements that need to be called
    current_directory = os.getcwd()
    element_info = gather_element_info(current_directory)
    elements_to_call = find_elements_to_load(html, extracted_elements, element_info)
    question_panel_keys = ["pl-question-panel","pl-matrix-latex", "pl-figure", "pl-card"]


def main(html: str,data:pl.QuestionData,isTesting=True):
    # Extracted elements is needed as this will be the original order of the html 
    extracted_elements = extract_valid_elements_from_html(html, valid_elements=VALID_ELEMENTS)
    print(extracted_elements)
    current_directory = os.getcwd()
    element_info = gather_element_info(current_directory)
    
    # Print extracted elements with better formatting
    print("\n--- Extracted Elements from HTML ---")
    for tag, content in extracted_elements.items():
        print(f"Tag: {tag}")
        for item in content:
            print(f"Content: {item}")
        print()  # Add extra line for better readability between tags
    
    # Print the current directory
    print("\n--- Current Directory ---")
    print(f"Directory Path: {current_directory}\n")
    
    # Print the element info
    print("\n--- Element Information ---")
    for element, info in element_info.items():
        print(f"Element {element} \n Info: {info}\n")

    elements_to_call = find_elements_to_load(html,extracted_elements,element_info)
    print(f"Elements to call {elements_to_call}")

    load_controllers(element_info=element_info,elements_to_call=elements_to_call)

    print(f"START ANALYSIS\n{'-'*40}\n")
    html = format_question_html(html,data=data,isTesting=isTesting)

    return html


## These are just functions for generating stuff for the correct answers to test the matrix input
def generate_mat(n: int) -> str:
        """
        Generates a random matrix of size n x n and converts it to JSON format.
        
        Args:
            n (int): Size of the matrix (n x n).
        
        Returns:
            str: JSON representation of the matrix.
        """
        mat = np.random.random((n, n))
        return pl.to_json(mat) # type: ignore

# Function to generate a symbolic expression using sympy
def generate_sym() -> str:
    """
    Generates a simple symbolic expression and converts it to JSON format.
    
    Returns:
        str: JSON representation of the symbolic expression.
    """
    x, y = sympy.symbols("x y")
    z = x + y + 1
    return pl.to_json(z) # type: ignore

if __name__ == "__main__":
    # Function to generate random matrices (3x3 and 2x2 for this example)
    mat_a = generate_mat(3)  # Generate a 3x3 matrix
    mat_b = generate_mat(2)  # Generate a 2x2 matrix
    
    # Parameters and correct answers for a projectile motion question (placeholders for now)
    # Parameters for the projectile motion question
    params = {
        "velocity": "20",  # Initial velocity of the projectile in m/s
        "angle": "45",    # Launch angle in degrees
        "matrixC": generate_mat(4),  # 4x4 matrix representing force components during flight
    }

    # Correct answers for the projectile motion question
    correct_answers = {
        "range": "120.45",  # Horizontal range of the projectile in meters
        "maxHeight": "22.5",  # Maximum height of the projectile in meters
        "flightTime": "10.5s",  # Total flight time of the projectile
        "forceComponents": generate_mat(3),  # Matrix A representing force components
        "matrixB": generate_mat(2),  # Final force components matrix B after impact
        "rangeExpression": r"v_0^2 \sin(2*theta) / g",  # Symbolic expression for horizontal range
        "timeFormula": r"t = \frac{2v_0 \sin \theta}{g}",  # Correct time formula
        "projectileType": {
            "Bullet": "Projectile in vacuum",
            "Basketball": "Projectile with air resistance",
            "Missile": "Guided projectile"
        },
        "motion-stages": ["Launch", "Peak height", "Descent", "Impact"]
    }

    
    # Constructing the data dictionary for the question
    data: pl.QuestionData = {
        "params": params,
        "correct_answers": correct_answers,
        "submitted_answers": {},  # Empty initially
        "format_errors": {},
        "partial_scores": {},
        "score": 0,
        "feedback": {"comment": "Great job"},  # Feedback placeholder
        "variant_seed": "seed123",  # Random seed
        "options": {},
        "raw_submitted_answers": {},
        "editable": True,  # Marks whether the question is editable
        "panel": "question",  # Initial panel for displaying the question
        "extensions": {},
        "num_valid_submissions": 3,  # Number of valid submissions allowed
        "manual_grading": False,  # No manual grading needed
        "answers_names": {}
    }

    # HTML template for the projectile motion question
    projectile_motion_question = r"""
        <pl-question-panel>
        <p>A projectile is launched with an initial velocity of {{params.velocity}} m/s at an angle of {{params.angle}} degrees above the horizontal.</p>
        <p>Assume no air resistance and a gravitational acceleration of 9.8 m/s². Based on the data provided, answer the following questions:</p>
        <ol>
            <li>Calculate the maximum height reached by the projectile.</li>
            <li>Determine the total time the projectile spends in the air.</li>
            <li>Calculate the horizontal range of the projectile.</li>
        </ol>
        <pl-figure file-name="projectile_motion.png"></pl-figure> <!-- Projectile motion diagram -->
        <p>The force components acting on the projectile during flight are represented by matrix \( C \), shown below:</p>
    <pl-matrix-latex params-name="matrixC" presentation-type="sigfig"></pl-matrix-latex>
    <p>Provide your calculated answers below:</p>
    </pl-question-panel>

    <pl-number-input answers-name="maxHeight" comparison="sigfig" digits="3" label="Maximum Height (in meters)"></pl-number-input>
    <pl-units-input answers-name="flightTime" atol="2s" label="Flight Time (in seconds)"></pl-units-input>
    <pl-number-input answers-name="range" comparison="sigfig" digits="3" label="Horizontal Range (in meters)"></pl-number-input>

    <p>Enter the symbolic expression for the horizontal range in terms of \( v_0 \) (initial velocity), \( \theta \) (angle), and \( g \) (gravitational constant):</p>
    <pl-symbolic-input answers-name="rangeExpression" variables="v_0, theta, g" label="Symbolic expression for horizontal range"></pl-symbolic-input>
    
    <p>Select the correct formula for the total flight time of the projectile:</p>
    <pl-checkbox answers-name="timeFormula" weight="1" inline="true">
        <pl-answer correct="true">\( t = \frac{2v_0 \sin \theta}{g} \)</pl-answer>
        <pl-answer correct="false">\( t = \frac{v_0 \cos \theta}{g} \)</pl-answer>
        <pl-answer correct="false">\( t = \frac{v_0^2}{g} \)</pl-answer>
        <pl-answer correct="false">\( t = \frac{v_0 \cdot g}{\sin \theta} \)</pl-answer>
    </pl-checkbox>
    

    <p>Matrix \( A \) represents the force components acting on the projectile at different points in its trajectory. Enter the values for matrix \( A \) below:</p>
    <pl-matrix-component-input answers-name="forceComponents" label="$A=$"></pl-matrix-component-input>

    <p>Matrix \( B \) represents the resulting forces after the projectile’s impact. Input the values for matrix \( B \) below:</p>
    <pl-matrix-input answers-name="matrixB" label="$B=$"></pl-matrix-input>

    <p>Match the following types of projectiles with their correct classification based on their motion:</p>
    <pl-matching answers-name="projectileType">
    <pl-statement match="Bullet">Projectile in vacuum</pl-statement>
    <pl-statement match="Basketball">Projectile with air resistance</pl-statement>
    <pl-statement match="Missile">Guided projectile</pl-statement>

    <pl-option>Guided projectile</pl-option>
    <pl-option>Projectile in vacuum</pl-option>
    <pl-option>Projectile with air resistance</pl-option>
    </pl-matching>

    <p>Arrange the following stages of projectile motion in the correct order:</p>
    <pl-order-blocks answers-name="motion-stages">
    <pl-answer correct="true">Launch</pl-answer>
    <pl-answer correct="true">Peak height</pl-answer>
    <pl-answer correct="true">Descent</pl-answer>
    <pl-answer correct="true">Impact</pl-answer>
    </pl-order-blocks>
    """

    
    # Path to save the generated HTML for the question
    question_html_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\test_html.html"
    
    # Write the HTML content of the question to a file
    with open(question_html_path, "w") as f:
        f.write(main(html=projectile_motion_question, data=data))  # Render the question page with the provided data

    # Update submitted answers (these are the student's answers)
    submitted_answers = {
        "range": "5",
        "maxHeight": "10",
        "flightTime": "25s",
        "forceComponents": generate_mat(3),  # Generate new matrices for submission
        "matrixB": generate_mat(2),
        "symbolic_math": generate_sym(),
        "rangeExpression": "v_0"
    }

    # Update the data dictionary with the submitted answers
    data["submitted_answers"] = submitted_answers
    data["panel"] = "answer"  # Switch to the answer panel

    # Path to save the HTML for the correct answers
    correct_html_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\correct_html.html"
    
    # Write the HTML content with the submitted answers to a file
    with open(correct_html_path, "w") as f:
        f.write(main(html=projectile_motion_question, data=data))  # Render the page with submitted answers

    # Switch the panel to submission mode for final review
    data["panel"] = "submission"
    
    # Path to save the HTML for the submission review
    sub_html_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\sub_html.html"
    
    # Write the final HTML content for the submission panel to a file
    with open(sub_html_path, "w") as f:
        f.write(main(html=projectile_motion_question, data=data))  # Render the final submission page

    # Print the final data for debugging purposes
    print(data)

    print(f"\nThese are the format errrors {data.get('format_errors')}\n")

    # def new_extract_element(html:str):
    #     extracted_content: dict[str, list] = {}
    #     tree = lxml.html.fromstring(html)
    #     for element in tree.iter():
    #         if element.tag in VALID_ELEMENTS:
    #             print(tree.find(element.tag))
    # new_extract_element(html = projectile_motion_question)
