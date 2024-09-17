import os
import json
import lxml.html
from lxml import etree
import numpy as np
import sympy
import html
import re

# Local module imports
from ..prairielearn.python import prairielearn as pl
from .dynamic_loader import load_module_from_path, run_controller, load_controllers

# Initialize logger
from ..logging_config.logging_config import get_logger
logger = get_logger(__name__)


# Define valid elements
VALID_ELEMENTS: list[str] = [
    "pl-question-panel", "pl-number-input", "pl-checkbox", "pl-figure", 
    "pl-integer-input", "pl-matching", "pl-matrix-component-input", 
    "pl-matrix-input", "pl-multiple-choice", "pl-order-blocks", 
    "pl-symbolic-input", "pl-units-input","pl-matrix-latex","pl-card","pl-answer-panel"
]
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

def find_elements_to_load(html_str: str, element_info: dict[str, dict[str, str]], extracted_elements=None):
    """
    Function to find and extract valid elements from the HTML, add them to a set, and modify the DOM.

    Args:
        html (str): The HTML fragment to process.
        element_info (dict[str, dict[str, str]]): Information about each valid element.
        extracted_elements (set): Set of extracted elements (to avoid duplication).
    """
    # Initialize the set if not passed
    if extracted_elements is None:
        extracted_elements = set()

    # Parse the HTML string into an element tree
    root = lxml.html.fromstring(html_str)

    # Iterate over elements in the parsed tree
    for element in root.iter():
        if element.tag in VALID_ELEMENTS:
            # Find valid child elements
            valid_children = [child for child in element if child.tag in VALID_ELEMENTS]

            # If there are valid children, add them to the set and recurse
            if len(valid_children) != 0:
                extracted_elements.add(element.tag)  # Add the parent tag
                for child in valid_children:
                    extracted_elements.add(child.tag)  # Add child tag
                    # Recursively process the child element itself
                    find_elements_to_load(etree.tostring(child), element_info, extracted_elements)
            else:
                # Add the element if it has no valid children
                extracted_elements.add(element.tag)

    # Get the intersection of extracted elements and element_info keys
    elements_to_call = extracted_elements & set(element_info.keys())

    return elements_to_call, extracted_elements

def process_extracted_elements(
    html_str: str, 
    filtering_elements: list[str], 
    data: 'pl.QuestionData', 
    controllers: dict, 
    custom_component=None
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
    html_str = f"<div>{html_str}</div>"
    tree = lxml.html.fromstring(html_str)
    processed_elements = set()

    def process_element(element, tree_root):
        """Recursive function to process element and its valid children."""
        valid_children = [child for child in element if child.tag in filtering_elements]

        # Recursively process valid children first
        for child in valid_children:
            if child not in processed_elements:
                process_element(child, tree_root)

        # Now process the parent element
        controller = controllers.get(element.tag)
        if controller:
            logger.debug(f"Running controller for element '{element.tag}': {controller}")
        else:
            logger.warning(f"No controller found for element '{element.tag}'")

        # Prepare and render the element
        element_html = etree.tostring(element, encoding='unicode') # type: ignore
        run_controller(controller, "prepare", element_html=element_html, data=data) # type: ignore
        rendered_html = run_controller(controller, "render", element_html=element_html, data=data) # type: ignore

        # Mark element as processed
        processed_elements.add(element)

        # If valid rendered HTML is returned, wrap it in custom component or use raw rendered HTML
        if rendered_html and isinstance(rendered_html, str):
            if custom_component:
                rendered_html = custom_component.format(content=rendered_html)

            # Get the parent of the element within the entire tree (not just its subtree)
            parent = element.getparent()
            if parent is not None:
                index = parent.index(element)

                # Remove the element from its parent in the entire tree
                parent.remove(element)
                if index == 0:
                    parent.text = (parent.text or "") + rendered_html
                else:
                    prev_sibling = parent[index - 1]
                    prev_sibling.tail = (prev_sibling.tail or "") + rendered_html
            else:
                logger.warning(f"The element '{element.tag}' has no parent to replace in the root tree.")
        else:
            logger.error(f"Invalid rendered HTML for element '{element.tag}': {rendered_html}")

    # Collect the elements to process after traversal
    elements_to_process = [e for e in tree.iter() if e.tag in filtering_elements and e not in processed_elements]

    # Process all collected elements and ensure we're working with the entire tree
    for e in elements_to_process:
        process_element(e, tree)

    # Return the modified HTML as a string
    try:
        modified_html = etree.tostring(tree, pretty_print=True).decode('utf-8') # type: ignore
    except UnicodeDecodeError as e:
        raise ValueError(f"Decoding error while converting the tree to a string: {e}")

    return modified_html





def main():
    current_dir = os.getcwd()
    
    # Gather element information
    element_info = gather_element_info(current_dir)
    print("Element Information Gathered:")
    for element, info in element_info.items():
        print(f"Element: {element}\nInfo: {info}\n")
    
    # Define the HTML content for the quiz (html_content)
    html_content = r"""
    <pl-card>
        <p>Provide your calculated answers below:</p>
        <pl-number-input answers-name="maxHeight" comparison="sigfig" digits="3" label="Maximum Height (in meters)"></pl-number-input>
        <pl-units-input answers-name="flightTime" atol="2s" label="Flight Time (in seconds)"></pl-units-input>
        <pl-number-input answers-name="range" comparison="sigfig" digits="3" label="Horizontal Range (in meters)"></pl-number-input>
    </pl-card>

    <pl-card>
        <p>Enter the symbolic expression for the horizontal range in terms of \( v_0 \) (initial velocity), \( \theta \) (angle), and \( g \) (gravitational constant):</p>
        <pl-symbolic-input answers-name="rangeExpression" variables="v_0, theta, g" label="Symbolic expression for horizontal range"></pl-symbolic-input>
    </pl-card>

    <pl-card>
        <p>Select the correct formula for the total flight time of the projectile:</p>
        <pl-checkbox answers-name="timeFormula" weight="1" inline="true">
            <pl-answer correct="true">\( t = \frac{2v_0 \sin \theta}{g} \)</pl-answer>
            <pl-answer correct="false">\( t = \frac{v_0 \cos \theta}{g} \)</pl-answer>
            <pl-answer correct="false">\( t = \frac{v_0^2}{g} \)</pl-answer>
            <pl-answer correct="false">\( t = \frac{v_0 \cdot g}{\sin \theta} \)</pl-answer>
        </pl-checkbox>
    </pl-card>

    <pl-card>
        <p>Matrix \( A \) represents the force components acting on the projectile at different points in its trajectory. Enter the values for matrix \( A \) below:</p>
        <pl-matrix-component-input answers-name="forceComponents" label="$A=$"></pl-matrix-component-input>
    </pl-card>

    <pl-card>
        <p>Matrix \( B \) represents the resulting forces after the projectile’s impact. Input the values for matrix \( B \) below:</p>
        <pl-matrix-input answers-name="matrixB" label="$B=$"></pl-matrix-input>
    </pl-card>

    <pl-card>
        <p>Match the following types of projectiles with their correct classification based on their motion:</p>
        <pl-matching answers-name="projectileType">
            <pl-statement match="Bullet">Projectile in vacuum</pl-statement>
            <pl-statement match="Basketball">Projectile with air resistance</pl-statement>
            <pl-statement match="Missile">Guided projectile</pl-statement>

            <pl-option>Guided projectile</pl-option>
            <pl-option>Projectile in vacuum</pl-option>
            <pl-option>Projectile with air resistance</pl-option>
        </pl-matching>
    </pl-card>

    <pl-card>
        <p>Arrange the following stages of projectile motion in the correct order:</p>
        <pl-order-blocks answers-name="motion-stages">
            <pl-answer correct="true">Launch</pl-answer>
            <pl-answer correct="true">Peak height</pl-answer>
            <pl-answer correct="true">Descent</pl-answer>
            <pl-answer correct="true">Impact</pl-answer>
        </pl-order-blocks>
    </pl-card>
    """
    
    # Define the HTML content for the question panel (html_content2)
    html_content2 = r"""
    <pl-question-panel>
        <p>A projectile is launched with an initial velocity of {{params.velocity}} m/s at an angle of {{params.angle}} degrees above the horizontal.</p>
        <p>Assume no air resistance and a gravitational acceleration of 9.8 $m/s^2$. Based on the data provided, answer the following questions:</p>
        <ol>
            <li>Calculate the maximum height reached by the projectile.</li>
            <li>Determine the total time the projectile spends in the air.</li>
            <li>Calculate the horizontal range of the projectile.</li>
        </ol>
        <p>The force components acting on the projectile during flight are represented by matrix \( C \), shown below:</p>
        <pl-matrix-latex params-name="matrixC" presentation-type="sigfig"></pl-matrix-latex>
    </pl-question-panel>
    """
    
    # Wrap the question panel in a pl-card
    html_content2_wrapped = f"""
    <pl-card>
        {html_content2}
    </pl-card>
    """
    
    # Process both HTML contents separately
    elements_to_call1, extracted_elements1 = find_elements_to_load(html_str=html_content, element_info=element_info)
    elements_to_call2, extracted_elements2 = find_elements_to_load(html_str=html_content2_wrapped, element_info=element_info)
    
    print("Elements to Call (html_content):")
    for element in elements_to_call1:
        print(f" - {element}")

    print("Elements to Call (html_content2_wrapped):")
    for element in elements_to_call2:
        print(f" - {element}")

    # Load controllers for both sets of elements
    controllers1 = load_controllers(element_info, elements_to_call1)
    controllers2 = load_controllers(element_info, elements_to_call2)
    
    # Parameters for the projectile motion question
    params = {
        "velocity": "20",  # Initial velocity of the projectile in m/s
        "angle": "45",     # Launch angle in degrees
        "matrixC": generate_mat(4),  # 4x4 matrix representing force components during flight
    }
    
    x = sympy.var("x")
    
    # Correct answers for the projectile motion question
    correct_answers = {
        "range": "120.45",  # Horizontal range of the projectile in meters
        "maxHeight": "22.5",  # Maximum height of the projectile in meters
        "flightTime": "10.5s",  # Total flight time of the projectile
        "forceComponents": generate_mat(3),  # 3x3 Matrix A representing force components
        "matrixB": generate_mat(2),  # 2x2 Matrix B representing force components after impact
        "rangeExpression": pl.to_json(x**2 + x + 1),  # Symbolic expression for horizontal range # type: ignore
        "projectileType": {
            "Bullet": "Projectile in vacuum",
            "Basketball": "Projectile with air resistance",
            "Missile": "Guided projectile"
        },
        "motion-stages": ["Launch", "Peak height", "Descent", "Impact"]  # Stages of motion
    }
    
    # Construct the data dictionary for the question
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
    
    # Process the first set of HTML content (html_content)
    modified_html1 = process_extracted_elements(
        html_str=html_content, 
        filtering_elements=list(extracted_elements1),
        data=data, 
        controllers=controllers1
    )
    
    # Process the second set of HTML content (html_content2_wrapped)
    modified_html2 = process_extracted_elements(
        html_str=html_content2_wrapped, 
        filtering_elements=list(extracted_elements2),
        data=data, 
        controllers=controllers2
    )

    # Unescape both HTML contents
    header = r"""
     <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
            <link rel="stylesheet" href="styles.css">
        </head>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
        <script src="../prairielearn/elements/pl-order-blocks/pl-order-blocks.js"></script>
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
    

    combined_html1 = header + html.unescape(html.unescape(modified_html1))
    combined_html2 = header + html.unescape(modified_html2)

    # Save both HTML files
    question_simple_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\simple.html"
    question_panel_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\question_panel.html"
    
    with open(question_simple_path, "w", encoding="utf-8") as f1:
        f1.write(combined_html1)  # Save first HTML content
    
    with open(question_panel_path, "w", encoding="utf-8") as f2:
        f2.write(combined_html2)  # Save second HTML content

    print(f"HTML content saved to {question_simple_path} and {question_panel_path}")


    full_html = html_content2_wrapped+html_content
    elements_to_call_full, extracted_elements_full = find_elements_to_load(html_str=full_html, element_info=element_info)
    controllers_full = load_controllers(element_info, elements_to_call_full)

    modified_html3 = process_extracted_elements(
        html_str=full_html, 
        filtering_elements=list(extracted_elements_full),
        data=data, 
        controllers=controllers_full
    )
    combined_html3 = header + html.unescape(html.unescape(modified_html3))
    full_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\full.html"
    with open(full_path, "w", encoding="utf-8") as f2:
        f2.write(combined_html3)  # Save second HTML content

if __name__ == "__main__":
    main()
