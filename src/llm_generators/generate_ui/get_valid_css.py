import json
import os 
print(os.getcwd())
from .ui_type import UIType


# Base directory where your script is running
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the JSON file
css_styles_file = os.path.join(base_dir, 'valid_css_styles_bootstrap.json')

with open(css_styles_file,"r") as file:
    css_styles = json.load(file)
def get_valid_css_classes( UItype: UIType,name_interest: str="",) -> tuple:
    """
    Helper function to isolate and retrieve valid CSS classes based on the specified UI type.

    Args:
        name_interest (str): The category name of the CSS styles (e.g., "summary_and_key_concepts").
        UItype (UIType): The UI type for which CSS classes are being isolated.

    Returns:
        tuple: A tuple containing:
            - VALID_CSS_STYLES (dict): A dictionary mapping UI types to their corresponding valid CSS class names.
            - css_descriptions (str): A formatted string containing descriptions of the valid CSS classes.
    """

    # Dictionary to store valid CSS classes based on the UI type
    VALID_CSS_STYLES = {}

    # String to accumulate descriptions of the CSS classes
    css_descriptions = ""

    # Retrieve the CSS styles for the specific category of interest
    selected_css_styles = css_styles.get(name_interest)

    # Retrieve the general CSS styles applicable across all categories
    generic_css_styles = css_styles.get("general_styles")
    if selected_css_styles:
    # Combine specific and general CSS styles into one dictionary
        available_styles = {**selected_css_styles, **generic_css_styles}
    else:
        available_styles={**generic_css_styles}

    # Iterate over the combined styles and filter based on UI type
    for uitype, css_items in available_styles.items():
        if uitype in UIType.__members__:
            css_class_names = []
            css_descriptions += f"\nUI Type: {uitype}\n"
            for css_item in css_items:
                css_class_name = css_item.get("name")
                css_class_names.append(css_class_name)
                description = css_item.get("description", "")
                css_descriptions += f"- {css_class_name}: {description}\n"
            # Add valid CSS classes to the dictionary for the given UI type
            VALID_CSS_STYLES[UIType[uitype]] = css_class_names

    # Return the dictionary of valid CSS classes and the accumulated descriptions
    return VALID_CSS_STYLES, css_descriptions


if __name__ == "__main__":
    u = UIType
    print(get_valid_css_classes(UItype=u))