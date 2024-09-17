import os
import json
import asyncio
from enum import Enum
from pydantic import BaseModel, Field, field_validator, validator
from typing import List, Tuple, Dict
from ...logging_config.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

# Set base directory and path to the CSS styles file
base_dir = os.path.dirname(os.path.abspath(__file__))
css_styles_file = os.path.join(base_dir, 'valid_css_styles_bootstrap.json')

# Load valid CSS styles from the JSON file
try:
    with open(css_styles_file, "r") as file:
        css_styles = json.load(file)
    logger.info("Successfully loaded CSS styles.")
except Exception as e:
    logger.error(f"Error loading CSS styles file: {e}")
    css_styles = {}
class UIType(str,Enum):
        div= "div"
        p = "p"
        ul = "ul"
        ol = "ol"
        li = "li"
        span = "span"
        strong = "strong"
        pl_question_panel = 'pl-question-panel'
        pl_number_input = "pl-number-input"
        pl_checkbox = "pl-checkbox"
        pl_figure = "pl-figure"
        pl_integer_input = "pl-integer-input"
        pl_matching = "pl-matching"
        pl_matrix_component_input = "pl-matrix-component-input"
        pl_multiple_choice = "pl-multiple-choice"
        pl_symbolic_input = "pl-symbolic-input"
        pl_units_input = "pl-units-input"
        pl_card = "pl-card"
        pl_statement = "pl-statement"
        pl_option = "pl-option"
        pl_answer = "pl-answer"


class Attribute(BaseModel):
        name: str = Field(..., description="Name of html attribute")
        value: str = Field(..., description="Value of the html attribute ")
class UI(BaseModel):
    type: UIType
    label: str = Field(
        ..., 
        description="Content to be placed inside HTML tags. If you need to write mathematical symbols or equations, use LaTeX enclosed within `$...$` for inline math or `$$...$$` for display math to ensure compatibility with the HTML file."
    )
    children: List["UI"]
    attributes: List[Attribute]
    _valid_css: Dict[UIType, List[str]] = {}

    @classmethod
    def set_valid_css(cls, category_interest: str = None):  # type: ignore
        cls._valid_css = {}  # Resetting the valid CSS dictionary
        selected_css_styles = css_styles.get(category_interest, {})
        generic_css_styles = css_styles.get("general_styles", {})

        # Combine selected and generic styles
        available_styles = {**selected_css_styles, **generic_css_styles}

        for uitype, css_items in available_styles.items():
            if uitype in UIType.__members__:
                css_classes = []
                for css_item in css_items:
                    css_class_name = css_item.get("name", "")
                    css_classes.append(css_class_name)
                cls._valid_css[UIType[uitype]] = css_classes

    @validator('attributes', each_item=True)
    def validate_attributes(cls, attr, values):
        ui_type = values.get('type')
        if attr.name == "class":
            valid_css_classes = cls._valid_css.get(ui_type, set())

            # Checks for cases where a class like "container my-5" is valid
            if attr.value in valid_css_classes:
                return attr

            # Splits the class attribute into individual classes
            class_names = attr.value.split()
            valid_class_names = [name for name in class_names if name in valid_css_classes]

            if not valid_class_names:
                logger.warning(f"Invalid CSS classes '{attr.value}' for UI type '{ui_type}'")
                attr.value = None  # or set it to an empty string or valid default
            else:
                attr.value = " ".join(valid_class_names)  # Join the list of attributes
        return attr

    @classmethod
    def get_valid_css(cls):
        return cls._valid_css

def get_css_description(UItype: UIType,category_interest):
    css_descriptions = ""
    selected_css_styles = css_styles.get(category_interest, {})
    generic_css_styles = css_styles.get("general_styles", {})
    # Combine selected and generic styles
    available_styles = {**selected_css_styles, **generic_css_styles}
    for uitype, css_items in available_styles.items():
         if uitype in UIType.__members__:
             for css_item in css_items:
                css_descriptions += f"\nUI Type: {uitype}\n"
                css_class_name = css_item.get("name")
                description = css_item.get("description", "")
                css_descriptions += f"- {css_class_name}: {description}\n"
    return css_descriptions


async def main():
    # Set valid CSS for the UI class with a specific category
    print("Setting valid CSS for the UI class with the category 'summary_and_key_concepts'.")
    UI.set_valid_css("summary_and_key_concepts")

    # Retrieve and print the valid CSS classes that have been set
    valid_css = UI.get_valid_css()
    print("Valid CSS classes set for each UI type:")
    for ui_type, css_classes in valid_css.items():
        print(f"  {ui_type}: {css_classes}")

    # Print the JSON schema for the UI model
    print("\nJSON schema for the UI model:")
    schema = UI.model_json_schema()
    print(schema)

if __name__ == "__main__":
    print("Starting the asynchronous main function.")
    asyncio.run(main())
    print("Finished running the asynchronous main function.")            