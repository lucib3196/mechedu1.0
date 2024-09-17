from .plutilities_new import TagReplacer
from typing import List, Dict
from  bs4 import BeautifulSoup
import pandas as pd
tag_replacer_configs = {
    "pl_question_panel": {
        "target_tag": "pl-question-panel",
        "replacement_tag": "div",
        "attributes": {
            "class": "card mb-4 p-3 bg-light"
        },
        "css_descriptions": [
            {
                "name": "card",
                "description": "Used to create a bordered box for the question panel."
            },
            {
                "name": "mb-4",
                "description": "Adds margin below the panel for spacing."
            },
            {
                "name": "p-3",
                "description": "Provides padding inside the panel for better content separation."
            },
            {
                "name": "bg-light",
                "description": "Applies a light background to the panel to distinguish it from other sections."
            }
        ],
        "mapping": {}
    },
    "pl_checkbox": {
        "target_tag": "pl-checkbox",
        "replacement_tag": "fieldset",
        "attributes": {
            "class": "form-check mb-3"
        },
        "css_descriptions": [
            {
                "name": "form-check",
                "description": "Styles the checkbox elements consistently."
            },
            {
                "name": "mb-3",
                "description": "Adds margin below the checkbox group to separate it from other content."
            }
        ],
        "mapping": {
            "answers-name": "answers-name",
            "weight": "data-weight",
            "inline": "data-inline"
        }
    },
    "pl_answer": {
        "target_tag": "pl-answer",
        "replacement_tag": "input",
        "attributes": {
            "type": "checkbox",
            "class": "form-check-input me-2"
        },
        "css_descriptions": [
            {
                "name": "form-check-input",
                "description": "Applies standard Bootstrap styling to checkbox inputs."
            },
            {
                "name": "me-2",
                "description": "Adds a small margin to the right of the checkbox for better spacing."
            }
        ],
        "mapping": {
            "correct": "data-correct"
        }
    },
    "pl_number_input": {
        "target_tag": "pl-number-input",
        "replacement_tag": "input",
        "attributes": {
            "type": "number",
            "size": "50",
            "value": "",
            "step": "any",
            "class": "form-control mb-2"
        },
        "css_descriptions": [
            {
                "name": "form-control",
                "description": "Styles the number input field consistently with other form controls."
            },
            {
                "name": "mb-2",
                "description": "Adds margin below the input field for spacing."
            }
        ],
        "mapping": {
            "answers-name": "answers-name",
            "id": "answers-name",
            "comparison": "comparison",
            "digits": "digits",
            "label": "label"
        }
    },
    "pl_solution_panel": {
        "target_tag": "pl-solution-panel",
        "replacement_tag": "div",
        "attributes": {
            "class": "alert alert-info p-3"
        },
        "css_descriptions": [
            {
                "name": "alert",
                "description": "Uses Bootstrap's alert component for a noticeable solution panel."
            },
            {
                "name": "alert-info",
                "description": "Styles the panel with an informational color (light blue)."
            },
            {
                "name": "p-3",
                "description": "Provides padding inside the solution panel for content spacing."
            }
        ],
        "mapping": {}
    },
    "pl_hint": {
        "target_tag": "pl-hint",
        "replacement_tag": "div",
        "attributes": {
            "class": "alert alert-warning p-3"
        },
        "css_descriptions": [
            {
                "name": "alert",
                "description": "Uses Bootstrap's alert component to highlight the hint."
            },
            {
                "name": "alert-warning",
                "description": "Styles the hint with a warning color (yellow) to draw attention."
            },
            {
                "name": "p-3",
                "description": "Adds padding inside the hint for better readability."
            }
        ],
        "mapping": {
            "data-type": "data-type",
            "level": "data-level"
        }
    },
    "pl_multiple_choice": {
        "target_tag": "pl-multiple-choice",
        "replacement_tag": "fieldset",
        "attributes": {
            "class": "card p-3 mb-3"
        },
        "css_descriptions": [
            {
                "name": "card",
                "description": "Wraps the multiple-choice group in a bordered container."
            },
            {
                "name": "p-3",
                "description": "Adds padding inside the multiple-choice container for better spacing."
            },
            {
                "name": "mb-3",
                "description": "Adds margin below the multiple-choice group for spacing."
            }
        ],
        "mapping": {
            "answers-name": "answers-name",
            "inline": "data-inline",
            "weight": "data-weight"
        }
    },
    "pl_text_input": {
        "target_tag": "pl-text-input",
        "replacement_tag": "input",
        "attributes": {
            "type": "text",
            "size": "50",
            "value": "",
            "class": "form-control mb-2"
        },
        "css_descriptions": [
            {
                "name": "form-control",
                "description": "Applies consistent styling to text input fields."
            },
            {
                "name": "mb-2",
                "description": "Adds margin below the text input field for spacing."
            }
        ],
        "mapping": {
            "answers-name": "answers-name",
            "label": "aria-label"
        }
    },
    "pl_figure": {
        "target_tag": "pl-figure",
        "replacement_tag": "img",
        "attributes": {
            "alt": "Picture for problem",
            "width": "300",
            "height": "300",
            "class": "img-fluid mx-auto d-block mb-3"
        },
        "css_descriptions": [
            {
                "name": "img-fluid",
                "description": "Makes the image responsive, adjusting its size based on the screen."
            },
            {
                "name": "mx-auto",
                "description": "Centers the image horizontally within its container."
            },
            {
                "name": "d-block",
                "description": "Ensures the image is displayed as a block-level element."
            },
            {
                "name": "mb-3",
                "description": "Adds margin below the image for spacing."
            }
        ],
        "mapping": {
            "file-name": "src"
        }
    },
    "pl_input_field": {
        "target_tag": "pl-input-field",
        "replacement_tag": "input",
        "attributes": {
            "type": "number",
            "size": "50",
            "value": "",
            "step": "any",
            "class": "form-control mb-2"
        },
        "css_descriptions": [
            {
                "name": "form-control",
                "description": "Styles the numeric input field to match other form elements."
            },
            {
                "name": "mb-2",
                "description": "Adds margin below the input field for spacing."
            }
        ],
        "mapping": {
            "variable-name": "name",
            "id": "variable-name",
            "label": "aria-label",
            "placeholder": "placeholder"
        }
    },
    "pl_input_panel": {
        "target_tag": "pl-input-panel",
        "replacement_tag": "div",
        "attributes": {
            "class": "card p-3 mb-3"
        },
        "css_descriptions": [
            {
                "name": "card",
                "description": "Creates a bordered panel to group input fields."
            },
            {
                "name": "p-3",
                "description": "Adds padding inside the input panel for better layout."
            },
            {
                "name": "mb-3",
                "description": "Adds margin below the input panel to separate it from other content."
            }
        ],
        "mapping": {}
    }
}




def create_tag_replacers(html_string: str, config: Dict[str, Dict]) -> List[TagReplacer]:
    replacers = []
    for name, cfg in config.items():
        replacer = TagReplacer(
            html=html_string,
            target_tag=cfg["target_tag"],
            replacement_tag=cfg["replacement_tag"],
            attributes=cfg["attributes"],
            mapping=cfg.get("mapping",{})
        )
        replacers.append(replacer)
    return replacers
def apply_tag_replacers(html_string: str, replacers: List[TagReplacer]) -> str:
    soup = BeautifulSoup(html_string, "html.parser")
    
    for replacer in replacers:
        print(f"Soup Before \n{soup}\n")
        replacer.update_soup(str(soup))
        soup = replacer.auto_replace()
        print(f"Soup After \n{soup}\n")
    return soup.prettify()

def run(html:str)->bool:
    replacers = create_tag_replacers(html, tag_replacer_configs)
    modified_html = apply_tag_replacers(html, replacers)
    print(modified_html)
    soup = BeautifulSoup(modified_html, "html.parser")
    all_tags = soup.find_all(True)
    for tag in all_tags:
            if tag.name.startswith("pl"):
                return True
    return False

def process_prairielearn_html(question_html: str, solution_html: str, qdata: dict, qname: str):
    pass

def main():
    path = r"C:\Users\lberm\OneDrive\Desktop\GitHub_Repository\mechedu1.0\mechedu1\src\utils\unique_tags.csv"
    df = pd.read_csv(path)
    print(df.head())
    for index, value in df["html"].items():
        print(run(value))
    df_to_fix = df[df["html"].apply(run)]
    print("This is the current df\n", df_to_fix["html"].iloc[0])
    print(df_to_fix["tag_name"])
    # # Create replacers from the config
    # replacers = create_tag_replacers(html_string, tag_replacer_configs)
    # # Apply the replacers to the HTML
    # modified_html = apply_tag_replacers(html_string, replacers)
    # print(modified_html)

    html = """
        <pl-question-panel> 
    <p>
        Action at a distance, such as is the case for gravity, was once thought to be illogical and therefore untrue. What is the ultimate determinant of the truth in science, and why was this action at a distance ultimately accepted?
    </p>
    </pl-question-panel>
    <pl-multiple-choice answers-name="actionAtDistance" weight="1" inline="true">
    <pl-answer correct="true">The ultimate determinant of the truth in science is empirical evidence. Action at a distance was ultimately accepted because it was supported by experimental observations and mathematical consistency.</pl-answer>
    <pl-answer correct="false">The ultimate determinant of the truth in science is logical consistency. Action at a distance was ultimately accepted because it was logically consistent with existing theories.</pl-answer>
    <pl-answer correct="false">The ultimate determinant of the truth in science is philosophical reasoning. Action at a distance was ultimately accepted because it aligned with philosophical principles.</pl-answer>
    <pl-answer correct="false">The ultimate determinant of the truth in science is consensus among scientists. Action at a distance was ultimately accepted because most scientists agreed on it.</pl-answer>
    </pl-multiple-choice>
    """
    replacers = create_tag_replacers(html, tag_replacer_configs)
    modified_html = apply_tag_replacers(html, replacers)
    print(modified_html)

if __name__ == "__main__":
    main()