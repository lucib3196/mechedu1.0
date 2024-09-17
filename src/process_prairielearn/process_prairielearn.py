from .extract import find_elements_to_load,gather_element_info,process_extracted_elements,generate_mat,generate_sym
from .dynamic_loader import load_controllers
from ..prairielearn.python import prairielearn as pl
import html
import os
import re
from jinja2 import Template
import sympy
# Define valid elements
VALID_ELEMENTS: list[str] = [
    "pl-question-panel", "pl-number-input", "pl-checkbox", "pl-figure", 
    "pl-integer-input", "pl-matching", "pl-matrix-component-input", 
    "pl-matrix-input", "pl-multiple-choice", "pl-order-blocks", 
    "pl-symbolic-input", "pl-units-input","pl-matrix-latex","pl-card","pl-answer-panel"
]
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


def format_question_html(html_content: str, data: 'pl.QuestionData', isTesting: bool = False) -> str:
    current_directory = os.getcwd()
    element_info = gather_element_info(current_directory,valid_elements=VALID_ELEMENTS)
    elements_to_call, extracted_elements = find_elements_to_load(html_str=html_content, element_info=element_info)
    controllers = load_controllers(element_info, elements_to_call)
    
    submitted_answers = data.get("submitted_answers",{})
    if (data.get('panel')=="answer") and (submitted_answers):
        answers = ""
        for k, v in submitted_answers.items():
            print(k,v)
  
    modified_html = process_extracted_elements(
        html_str=html_content, 
        filtering_elements=list(extracted_elements),
        data=data, 
        controllers=controllers
    )
    modified_html =  html.unescape(html.unescape(modified_html))
    if isTesting:
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
        modified_html = header + modified_html
    params = data.get("params", {})
    modified_html = Template(escape_jinja_in_latex(modified_html)).render(params=params)

    return modified_html

if __name__ == "__main__":
    projectile_motion_question = r"""
    <pl-card>
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
            <pl-answer-panel>
    </pl-card>

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
    </pl-card>"""

    params = {
        "velocity": "20",  # Initial velocity of the projectile in m/s
        "angle": "45",    # Launch angle in degrees
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
    question_html_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\test_html.html"
    # Write the HTML content to a file
    with open(question_html_path, "w", encoding="utf-8") as f:
        f.write(format_question_html(html_content=projectile_motion_question,data =data,isTesting=True))  # Render the question page with the provided data
    submitted_answers = {
        "range": 5,
        "maxHeight": 10,
        "flightTime": '25s',
        "forceComponents": generate_mat(3),  # Generate new matrices for submission
        "matrixB": generate_mat(2),
        "symbolic_math": generate_sym(),
        "rangeExpression": r'v_0^2 sin(2*theta) / g'
    }
    data["submitted_answers"] = submitted_answers
    data["panel"] = "answer"
    # Path to save the HTML for the correct answers
    correct_html_path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\process_prairielearn\correct_html.html"
    
    # Write the HTML content with the submitted answers to a file
    with open(correct_html_path, "w") as f:
        f.write(html.unescape(format_question_html(html_content=projectile_motion_question,data =data,isTesting=True)))  # Render the page with submitted answers