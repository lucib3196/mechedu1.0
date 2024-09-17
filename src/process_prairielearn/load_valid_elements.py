import os
import sys
import json
import importlib.util
import types


from lxml import html, etree
import lxml.html
from ..logging_config.logging_config import get_logger
from ..prairielearn.python import prairielearn as pl

# Initialize logger
logger = get_logger(__name__)


VALID_ELEMENTS: list[str] = ["pl-question-panel", "pl-number-input", "pl-checkbox", "pl-figure", "pl-integer-input","pl-matching","pl-matrix-component-input","pl-matrix-input","pl-multiple-choice","pl-order-blocks","pl-symbolic-input","pl-units-input"]
test_htmls = [
    r"""<pl-question-panel>
  <p>A ball is thrown horizontally from the top of a building with a height of {{params.height}} {{params.unitsDist}} with an initial speed of {{params.initialSpeed}} {{params.unitsSpeed}}. </p>
  <p>Assuming there is no air resistance, calculate the time it takes for the ball to reach the ground.</p>
</pl-question-panel>

<pl-number-input answers-name="t" comparison="sigfig" digits="3" label="Time (in seconds)"></pl-number-input>
<pl-number-input answers-name="w" comparison="sigfig" digits="3" label="Time (in seconds)"></pl-number-input>
<pl-number-input answers-name="z" comparison="sigfig" digits="3" label="Time (in seconds)"></pl-number-input>
    """,
    r"""<pl-question-panel>
    
  <p>The figure above illustrates concepts related to gases under certain conditions. Which of the following is the ideal gas law equation?</p>
  <pl-figure file-name="gas_laws.png"></pl-figure>
  <pl-number-input answers-name="t" comparison="sigfig" digits="3" label="Time (in seconds)"></pl-number-input>
</pl-question-panel>

<pl-checkbox answers-name="idealGas" weight="1" inline="true">
  <pl-answer correct="true">\( PV = nRT \)</pl-answer>
  <pl-answer correct="false">\( P = \rho RT \)</pl-answer>
  <pl-answer correct="false">\( P = \frac{m}{V} \)</pl-answer>
  <pl-answer correct="false">\( P = \frac{RT}{m} \)</pl-answer>
</pl-checkbox>
    """
]
data: pl.QuestionData = {
    "params": {"height": "5", "unitsDist":"m","initialSpeed":"5", "unitsSpeed":"m/s"},
    "correct_answers": {"t": "5"},
    "submitted_answers": {"t":None},  # Make sure the key matches the input name
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
# def load_element_info(base_dir: str, valid_elements: list[str]) -> dict:
#     loaded_modules = {}
#     elements_path = os.path.join(base_dir, 'src', "prairielearn", "elements")
    
#     # Log the elements path for debugging
#     logger.debug(f"Elements path: {elements_path}")

#     # Traverse through the directory structure
#     for root, dirs, files in os.walk(elements_path):
#         package_root = os.path.abspath(os.path.join(root, '..', '..'))
        
#         # Add package root to sys.path if not already present
#         if package_root not in sys.path:
#             sys.path.insert(0, package_root)
        
#         element_name = os.path.basename(root)
#         print(root)
#         if element_name in valid_elements:
#             try:
#                 # Load the info.json file
#                 info_path = os.path.join(root, "info.json")
#                 with open(info_path, 'r') as f:
#                     contents_dict = json.load(f)
#             except (json.JSONDecodeError, IOError) as e:
#                 logger.error(f"Error reading {info_path}: {e}")
#                 continue

#             # Extract controller and dependencies
#             controller = contents_dict.get("controller", "")
#             dependencies = contents_dict.get("dependencies", {})
#             element_styles = dependencies.get("elementStyles", [])
            
#             # Log the extracted data
#             logger.info(f"Controller: {controller}, Dependencies: {dependencies}, Element Styles: {element_styles}")
            
#             # Store the module-related information
#             loaded_module = {
#                 "elementStyles": element_styles
#             }
            
#             if controller:
#                 try:
#                     # Load the controller module dynamically
#                     spec = importlib.util.spec_from_file_location(element_name,os.path.join(root,controller))
#                     if spec and spec.loader:
#                         module = importlib.util.module_from_spec(spec)
#                         sys.modules[element_name] = module
#                         spec.loader.exec_module(module)
#                         loaded_module["module"] = module
#                         loaded_modules[element_name] = loaded_module
#                         # Log successful loading
#                         logger.info(f"Module {element_name} loaded successfully.")
#                     else:
#                         logger.error(f"Could not create spec or loader for module: {controller}")
#                 except Exception as e:
#                     logger.error(f"Error loading module {controller}: {e}")
#     return loaded_modules

# def extract_valid_elements_from_html(html: str, valid_elements: list[str]) -> dict:
#     extracted_content = {}
#     tree = lxml.html.fromstring(html)
    
#     for element in tree.iter():
#         # Check if the current element is one of the valid elements
#         if element.tag in valid_elements:
#             # Prepare a dictionary to collect child elements (if they exist)
#             collection = {}
            
#             # Iterate over the element's children to extract nested valid elements
#             for child in list(element):
#                 if child.tag in valid_elements:
#                     # Recursively extract valid elements from the child
#                     child_html = etree.tostring(child).decode('utf-8', errors='ignore')
#                     new_dict = extract_valid_elements_from_html(child_html, valid_elements)
                    
#                     # Remove the child after extraction
#                     element.remove(child)
                    
#                     # Merge the child dictionary into the collection
#                     for key, value in new_dict.items():
#                         if key in collection:
#                             collection[key].extend(value)
#                         else:
#                             collection[key] = value
            
#             # Convert the current element (without its already-extracted children) to string
#             extracted_html = etree.tostring(element).decode('utf-8', errors='ignore')
            
#             # Add the extracted element to the result
#             if element.tag in extracted_content:
#                 extracted_content[element.tag].append(extracted_html)
#             else:
#                 if collection:
#                     extracted_content[element.tag] = [extracted_html, collection]
#                 else:
#                     extracted_content[element.tag] = [extracted_html]
    
#     return extracted_content

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
            raise AttributeError(f"Function {function_name} not found in the module.")
    
    except Exception as e:
        print(f"Error: {e}")
        return None

def format_question_html(html_string: str, question_data: pl.QuestionData, valid_elements: list[str] = VALID_ELEMENTS) -> str:
    formatted_html = ""
    current_directory = os.getcwd()
    
    # Load all available element controllers from the specified directory
    element_controllers = load_element_info(current_directory, valid_elements)
    
    # Extract HTML elements that match the valid elements from the given HTML string
    extracted_elements = extract_valid_elements_from_html(valid_elements=valid_elements, html=html_string)
    
    # Filter out specific question panel elements
    question_panel_keys = ["pl-question-panel"]
    filtered_question_panels = {}
    for panel_key in question_panel_keys:
        if panel_key in extracted_elements:
            filtered_question_panels[panel_key] = extracted_elements.pop(panel_key)
    
    # Wrap the question for the students to view
    question_view = process_extracted_elements(html_string, question_data, element_controllers, filtered_question_panels)
    
    # Handle Answer Inputs 
    input_panel_keys = ["pl-number-input", "pl-checkbox", "pl-integer-input","pl-matching","pl-matrix-component-input","pl-matrix-input","pl-multiple-choice","pl-order-blocks","pl-symbolic-input","pl-units-input"]
    filtered_input_panels = {}
    for panel_key in input_panel_keys:
        if panel_key in extracted_elements:
            filtered_input_panels[panel_key] = extracted_elements.pop(panel_key)
    
    # Process the input form elements
    form_area = process_extracted_elements(html_string, question_data, element_controllers, filtered_input_panels)
    
    # Wrap the question view in Bootstrap's card component
    question_html = f"""
    <div class="card mb-3">
        <div class="card-header">
            Question
        </div>
        <div class="card-body">
            {question_view}
        </div>
    </div>
    """

    # Wrap the form elements with a Bootstrap form, including a submit button
    form_html = f"""
    <form method="post">
        <div class="form-group">
            {form_area}
        </div>
        <button type="submit" class="btn btn-primary mt-3">Submit</button>
    </form>
    """
    
    # Combine question and form in formatted_html
    formatted_html = question_html + form_html
    full = r"""
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{% block title %}Document Title{% endblock %}</title>

        <!-- Include Local CSS -->
        <link rel="stylesheet" href="styles.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">


        <!-- MathJax Configuration -->
        <script type="text/javascript">
            window.MathJax = {
                tex: {
                    inlineMath: [['$', '$'], ['\\(', '\\)']],
                    displayMath: [['$$', '$$'], ['\\[', '\\]']]
                }
            };
        </script>
        
        <!-- Include MathJax -->
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    </head>
    <body>
    """+ formatted_html
    return full



def process_extracted_elements(base_html: str, question_data: pl.QuestionData, element_controllers: dict, extracted_elements: dict, custom_component: str = None) -> str:
    # Determine which elements from the HTML are both extracted and have corresponding controllers
    extracted_element_keys = set(extracted_elements.keys())
    available_controller_keys = set(element_controllers.keys())
    formatted_html = ""
    for element_key in extracted_element_keys:
        if element_key in available_controller_keys:
            element_info = element_controllers[element_key]
            print(f"This is the element info {element_info}")
            
            controller = element_info.get("module", "")
            
            # Render and format the HTML using the controller's render method
            for html_content in extracted_elements[element_key]:
                print(html_content)
                if isinstance(html_content,dict):
                    formatted_html+=process_extracted_elements(base_html, question_data,element_controllers,html_content, custom_component=None)
                run_controller(controller, "prepare", element_html=html_content, data=question_data)
                rendered_html = run_controller(controller, "render", element_html=html_content, data=question_data)
                
                # Use custom component if provided, otherwise default component
                if rendered_html:
                    if custom_component:
                        formatted_component = custom_component.format(content=rendered_html)
                    else:
                        formatted_component = f"""
                            <div class="card m-3">
                                <div class="card-body">
                                    {rendered_html}
                                </div>
                            </div>
                        """
                
                    formatted_html += formatted_component
    return formatted_html

free_fall_question = r"""
<pl-question-panel>
  <p>A ball is dropped from a height of {{params.height}} meters. Assume that the ball falls freely under gravity (g = 9.8 m/s²) with no air resistance.</p>
  <ol>
    <li>Calculate the time it takes for the ball to reach the ground.</li>
    <li>Determine the velocity of the ball when it hits the ground.</li>
    <li>Calculate the potential energy lost during the fall.</li>
  </ol>
  <pl-figure file-name="free_fall.png"></pl-figure>
</pl-question-panel>

<!-- Number input for the time to reach the ground -->
<pl-number-input answers-name="time" comparison="sigfig" digits="3" label="Time (in seconds)"></pl-number-input>

<!-- Number input for the velocity at the ground -->
<pl-number-input answers-name="velocity" comparison="sigfig" digits="3" label="Velocity (in meters per second)"></pl-number-input>

<!-- Number input for potential energy lost -->
<pl-number-input answers-name="potentialEnergy" comparison="sigfig" digits="3" label="Potential Energy (in Joules)"></pl-number-input>

<!-- Multiple-choice question for the correct formula to calculate velocity -->
<pl-checkbox answers-name="velocityFormula" weight="1" inline="true">
  <pl-answer correct="true">\( v_f = \sqrt{2gh} \)</pl-answer>
  <pl-answer correct="false">\( v_f = g \cdot t \)</pl-answer>
  <pl-answer correct="false">\( v_f = mgh \)</pl-answer>
  <pl-answer correct="false">\( v_f = \frac{gh}{t} \)</pl-answer>
</pl-checkbox>

<!-- Symbolic input for the final velocity -->
<p>Express the final velocity in terms of height \( h \) and gravitational constant \( g \):</p>
<pl-symbolic-input answers-name="velocityExpression" variables="h, g" label="\( v_f = \)"></pl-symbolic-input>
"""
pendulum_question = r"""
<pl-question-panel>
  <p>A pendulum with a length of {{params.length}} meters swings with a small amplitude. Assume that the motion is simple harmonic and the gravitational acceleration is \( g = 9.8 \, \text{m/s}^2 \).</p>
  <ol>
    <li>Calculate the period of the pendulum.</li>
    <li>Determine the maximum speed of the pendulum at the lowest point.</li>
    <li>Calculate the maximum potential energy of the pendulum at its highest point.</li>
  </ol>
  <pl-figure file-name="pendulum_motion.png"></pl-figure>
</pl-question-panel>

<!-- Number input for the period of the pendulum -->
<pl-number-input answers-name="period" comparison="sigfig" digits="3" label="Period (in seconds)"></pl-number-input>

<!-- Number input for the maximum speed -->
<pl-number-input answers-name="maxSpeed" comparison="sigfig" digits="3" label="Maximum Speed (in meters per second)"></pl-number-input>

<!-- Number input for the maximum potential energy -->
<pl-number-input answers-name="maxPotentialEnergy" comparison="sigfig" digits="3" label="Maximum Potential Energy (in Joules)"></pl-number-input>

<!-- Multiple-choice question for the correct formula to calculate the period -->
<pl-checkbox answers-name="periodFormula" weight="1" inline="true">
  <pl-answer correct="true">\( T = 2\pi \sqrt{\frac{L}{g}} \)</pl-answer>
  <pl-answer correct="false">\( T = 2\pi \sqrt{\frac{g}{L}} \)</pl-answer>
  <pl-answer correct="false">\( T = \frac{2\pi}{g} \)</pl-answer>
</pl-checkbox>

<!-- Integer input for a different pendulum's period -->
<p>For a pendulum with a length of 2 meters, calculate its period:</p>
<pl-integer-input answers-name="newPeriod" label="Period (in seconds)"></pl-integer-input>

<pl-units-input answers-name="pendulum_length" correct-answer="2m" atol="1cm"></pl-units-input>
"""
ideal_gas_question = r"""
<pl-question-panel>
  <p>A gas is contained in a sealed cylinder with a volume of {{params.volume}} liters at a temperature of {{params.temperature}} Kelvin and a pressure of {{params.pressure}} atm. Assume the gas behaves ideally.</p>
  <ol>
    <li>Calculate the number of moles of gas in the cylinder using the ideal gas law \( PV = nRT \).</li>
    <li>Determine the volume of the gas if the pressure is doubled and temperature remains constant.</li>
    <li>Calculate the change in internal energy if the temperature is increased by 100 K.</li>
  </ol>
  <pl-figure file-name="ideal_gas.png"></pl-figure>
</pl-question-panel>

<!-- Number input for the number of moles -->
<pl-number-input answers-name="moles" comparison="sigfig" digits="3" label="Moles (in mol)"></pl-number-input>

<!-- Number input for the new volume when pressure is doubled -->
<pl-number-input answers-name="newVolume" comparison="sigfig" digits="3" label="New Volume (in liters)"></pl-number-input>

<!-- Number input for the change in internal energy -->
<pl-number-input answers-name="internalEnergyChange" comparison="sigfig" digits="3" label="Change in Internal Energy (in Joules)"></pl-number-input>

<!-- Multiple-choice question for the correct formula to calculate moles -->
<pl-checkbox answers-name="molesFormula" weight="1" inline="true">
  <pl-answer correct="true">\( n = \frac{PV}{RT} \)</pl-answer>
  <pl-answer correct="false">\( n = \frac{RT}{PV} \)</pl-answer>
  <pl-answer correct="false">\( n = PV \cdot T \)</pl-answer>
</pl-checkbox>

<!-- Matching question for gas laws -->
<p>Match the gas law to its description:</p>
<pl-matching answers-name="gasLaws">
  <pl-statement match="Boyle's Law">At constant temperature, the pressure of a gas is inversely proportional to its volume.</pl-statement>
  <pl-statement match="Charles's Law">At constant pressure, the volume of a gas is directly proportional to its temperature.</pl-statement>
  <pl-statement match="Ideal Gas Law">The relationship between pressure, volume, temperature, and the number of moles of a gas.</pl-statement>

  <pl-option>Boyle's Law</pl-option>
  <pl-option>Charles's Law</pl-option>
  <pl-option>Ideal Gas Law</pl-option>
</pl-matching>
"""
forces_and_friction_question = r"""
<pl-question-panel>
  <p>A block is placed on a rough horizontal surface. The block is pushed with a force of {{params.force}} N at an angle of {{params.angle}} degrees with the horizontal.</p>
  <p>The coefficient of kinetic friction between the block and the surface is {{params.frictionCoeff}}. Answer the following questions:</p>
  <ol>
    <li>Calculate the frictional force acting on the block.</li>
    <li>Determine the net force acting on the block in the horizontal direction.</li>
    <li>Calculate the acceleration of the block.</li>
  </ol>
  <pl-figure file-name="block_on_surface.png"></pl-figure>
</pl-question-panel>

<!-- Matrix input for force components -->
<p>Enter the force components in the horizontal and vertical directions (in N):</p>
<pl-matrix-input answers-name="forceComponents" label="Force Components (N)"></pl-matrix-input>

<!-- Number input for frictional force -->
<pl-number-input answers-name="frictionForce" comparison="sigfig" digits="3" label="Frictional Force (in N)"></pl-number-input>

<!-- Number input for net force -->
<pl-number-input answers-name="netForce" comparison="sigfig" digits="3" label="Net Force (in N)"></pl-number-input>

<!-- Number input for acceleration -->
<pl-number-input answers-name="acceleration" comparison="sigfig" digits="3" label="Acceleration (in m/s²)"></pl-number-input>

<!-- Ordering question for forces acting on the block -->
<p>List the forces acting on the block in order of magnitude:</p>
<pl-order-blocks answers-name="orderForces">
  <pl-answer correct="false">Gravitational Force</pl-answer>
  <pl-answer correct="true">Applied Force</pl-answer>
  <pl-answer correct="false">Normal Force</pl-answer>
  <pl-answer correct="true">Frictional Force</pl-answer>
</pl-order-blocks>
"""
projectile_motion_question = r"""
<pl-question-panel>
  <p>A projectile is launched with an initial velocity of {{params.velocity}} m/s at an angle of {{params.angle}} degrees above the horizontal.</p>
  <p>Assume no air resistance and a gravitational acceleration of 9.8 m/s². Answer the following questions:</p>
  <ol>
    <li>Calculate the maximum height reached by the projectile.</li>
    <li>Determine the total time the projectile spends in the air.</li>
    <li>Calculate the horizontal range of the projectile.</li>
  </ol>
  <pl-figure file-name="projectile_motion.png"></pl-figure>
</pl-question-panel>

<!-- Number input for maximum height -->
<pl-number-input answers-name="maxHeight" comparison="sigfig" digits="3" label="Maximum Height (in meters)"></pl-number-input>

<!-- Units input for time of flight -->
<p>Enter the time of flight with appropriate units:</p>
<pl-units-input answers-name="flightTime" correct-answer="10s" atol="0.1s"></pl-units-input>

<!-- Number input for horizontal range -->
<pl-number-input answers-name="range" comparison="sigfig" digits="3" label="Horizontal Range (in meters)"></pl-number-input>

<!-- Symbolic input for horizontal range formula -->
<p>Express the horizontal range in terms of the initial velocity \( v_0 \), launch angle \( \theta \), and gravitational acceleration \( g \):</p>
<pl-symbolic-input answers-name="rangeExpression" variables="v_0, theta, g" label="Horizontal Range"></pl-symbolic-input>

<!-- Multiple-choice question for the formula to calculate time of flight -->
<pl-checkbox answers-name="timeFormula" weight="1" inline="true">
  <pl-answer correct="true">\( t = \frac{2v_0 \sin \theta}{g} \)</pl-answer>
  <pl-answer correct="false">\( t = \frac{v_0 \cos \theta}{g} \)</pl-answer>
  <pl-answer correct="false">\( t = \frac{v_0^2}{g} \)</pl-answer>
  <pl-answer correct="false">\( t = \frac{v_0 \cdot g}{\sin \theta} \)</pl-answer>
</pl-checkbox>
"""
circular_motion_question = r"""
<pl-question-panel>
  <p>A car is moving in a circular path with a radius of {{params.radius}} meters at a constant speed of {{params.speed}} m/s. Assume the car experiences a centripetal force.</p>
  <p>Answer the following questions about the car's circular motion:</p>
  <ol>
    <li>Calculate the centripetal acceleration of the car.</li>
    <li>Determine the force acting on the car if its mass is {{params.mass}} kg.</li>
    <li>Calculate the time it takes for the car to complete one full revolution.</li>
  </ol>
  <pl-figure file-name="circular_motion.png"></pl-figure>
</pl-question-panel>

<!-- Number input for centripetal acceleration -->
<pl-number-input answers-name="centripetalAcceleration" comparison="sigfig" digits="3" label="Centripetal Acceleration (in m/s²)"></pl-number-input>

<!-- Number input for centripetal force -->
<pl-number-input answers-name="centripetalForce" comparison="sigfig" digits="3" label="Centripetal Force (in N)"></pl-number-input>

<!-- Integer input for time of revolution -->
<p>Calculate the time for one full revolution in seconds:</p>
<pl-integer-input answers-name="timeRevolution" label="Time (in seconds)"></pl-integer-input>

<!-- Multiple-choice question for the correct formula for centripetal acceleration -->
<pl-checkbox answers-name="centripetalAccelerationFormula" weight="1" inline="true">
  <pl-answer correct="true">\( a_c = \frac{v^2}{r} \)</pl-answer>
  <pl-answer correct="false">\( a_c = \frac{r^2}{v} \)</pl-answer>
  <pl-answer correct="false">\( a_c = v \cdot r \)</pl-answer>
  <pl-answer correct="false">\( a_c = \frac{v}{r^2} \)</pl-answer>
</pl-checkbox>

<!-- Matrix input for velocity and acceleration components -->
<p>Enter the velocity and acceleration components (in m/s and m/s²):</p>
<pl-matrix-input answers-name="motionComponents" label="Velocity and Acceleration Components"></pl-matrix-input>
"""
new_question_html = r"""
<pl-question-panel>
  <p>A car starts from rest at the top of a frictionless incline with an angle of {{params.angle}} degrees and a height of {{params.height}} meters.</p>
  <p>Assuming there is no friction, answer the following questions about the car's motion as it slides down the incline:</p>
  <ol>
    <li>Calculate the time it takes for the car to reach the bottom of the incline.</li>
    <li>Determine the velocity of the car when it reaches the bottom of the incline.</li>
    <li>Calculate the acceleration of the car along the incline.</li>
  </ol>
  <pl-figure file-name="inclined_plane.png"></pl-figure>
</pl-question-panel>

<!-- Number input for the time to reach the bottom -->
<pl-number-input answers-name="time" comparison="sigfig" digits="3" label="Time (in seconds)"></pl-number-input>

<!-- Number input for the velocity at the bottom -->
<pl-number-input answers-name="velocity" comparison="sigfig" digits="3" label="Velocity (in meters per second)"></pl-number-input>

<!-- Number input for acceleration -->
<pl-number-input answers-name="acceleration" comparison="sigfig" digits="3" label="Acceleration (in meters per second squared)"></pl-number-input>

<!-- Multiple-choice question for the correct velocity formula -->
<pl-checkbox answers-name="velocityFormula" weight="1" inline="true">
  <pl-answer correct="true">\( v_f = \sqrt{2gh} \)</pl-answer>
  <pl-answer correct="false">\( v_f = g \cdot t \)</pl-answer>
  <pl-answer correct="false">\( v_f = mgh \)</pl-answer>
  <pl-answer correct="false">\( v_f = \frac{gh}{t} \)</pl-answer>
</pl-checkbox>

<!-- Integer input for height of a new incline -->
<p>Given a new incline with a different height, calculate the time for the car to reach the bottom of a 10-meter incline:</p>
<pl-integer-input answers-name="newTime" label="Time (in seconds)"></pl-integer-input>

<!-- Matching question related to inclined planes and laws of motion -->
<p>Match the following physics principles with their correct descriptions:</p>
<pl-matching answers-name="physicsConcepts">
  <pl-statement match="Newton's Second Law">The net force acting on an object is equal to its mass times its acceleration.</pl-statement>
  <pl-statement match="Conservation of Energy">The total energy in an isolated system remains constant.</pl-statement>
  <pl-statement match="Kinetic Energy">The energy possessed by a body due to its motion.</pl-statement>

  <pl-option>Newton's First Law</pl-option>
  <pl-option>Conservation of Energy</pl-option>
  <pl-option>Kinetic Energy</pl-option>
  <pl-option>Newton's Second Law</pl-option>
</pl-matching>

<!-- Matrix input for calculating forces on the car along the incline -->
<p>Calculate the force components along and perpendicular to the incline:</p>
<pl-matrix-component-input answers-name="forceComponents" label="Force Components"></pl-matrix-component-input>

<!-- Multiple-choice question for acceleration direction -->
<p>What is the direction of the car's acceleration on the incline?</p>
<pl-multiple-choice answers-name="accelerationDirection" weight="1">
  <pl-answer correct="true">Down the incline</pl-answer>
  <pl-answer correct="false">Up the incline</pl-answer>
  <pl-answer correct="false">Perpendicular to the incline</pl-answer>
</pl-multiple-choice>

<!-- Ordering question for listing physics quantities -->
<p>List the following quantities in order of magnitude for the car's motion:</p>
<pl-order-blocks answers-name="orderQuantities">
  <pl-answer correct="false">Frictional Force</pl-answer>
  <pl-answer correct="true">Gravitational Force</pl-answer>
  <pl-answer correct="false">Air Resistance</pl-answer>
  <pl-answer correct="true">Normal Force</pl-answer>
</pl-order-blocks>

<pl-symbolic-input answers-name="symbolic_math" variables="x, y" label="$z =$"></pl-symbolic-input>

<pl-units-input answers-name="c_1" correct-answer="1m" atol="1cm"></pl-units-input>
"""
all_htmls = []
import numpy as np
from ..prairielearn.python import prairielearn as pl
def generate_mat(n):

    # Generate a random 3x3 matrix
    mat = np.random.random((n, n))

    # Answer to each matrix entry converted to JSON
    return pl.to_json(mat)
import sympy
def generate_sym():

    # Declare math symbols
    x, y = sympy.symbols("x y")

    # Describe the equation
    z = x + y + 1

    # Answer to fill in the blank input stored as JSON.
    return pl.to_json(z)

correct_answers = {
    "distance": "5",  # Check if the system expects string or numeric values
    "time": "10",     # Same here: ensure consistency with the expected data type
    "finalSpeed": "25", 
    "forceComponents": generate_mat(3),  # Ensure generate_mat() returns a valid matrix format
    "matrixB": generate_mat(2),          # Same for this matrix
    "symbolic_math": generate_sym()    # Ensure generate_sym() returns a valid symbolic expression
  # Correct units are used here, ensure the system expects this format
}
data: pl.QuestionData = {
    "params": {"height": "5", "unitsDist":"m","initialSpeed":"5", "unitsSpeed":"m/s"},
    "correct_answers":correct_answers,
    "submitted_answers": {},  # Make sure the key matches the input name
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
formatted_html = format_question_html(new_question_html, data)
print(f"Final html \n{formatted_html}")

test_html_path =   r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\test_html.html"
with open(test_html_path, "w") as f:
    f.write(formatted_html)




