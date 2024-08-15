import os
from bs4 import BeautifulSoup
# import mathhelper
from jinja2 import Template
from flask import url_for
import random
from ast import literal_eval

import os
from bs4 import BeautifulSoup
from jinja2 import Template

def pl_number_input(soup, tag_name: str, qdata: dict):
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("The 'soup' argument must be a BeautifulSoup object.")
    
    # Find all old tags that match the provided tag name
    old_tags = soup.find_all(tag_name)
    for old_tag in old_tags:
        # Extract attributes from the old tag
        attribute = old_tag.attrs
        answers_name = attribute.get("answers-name","")
        # print(f'This is comparison f{attribute.get("comparison")}')
        # Determine the correct answer value
        correct_answer = attribute.get('correct-answer') or qdata.get('correct_answers', {}).get(answers_name, '')

        # Create the visible input tag with dynamic attributes
        new_tag = soup.new_tag(
            name="input",
            attrs={
                "type": "number",
                "class": "response",
                "name": answers_name,
                "id": answers_name,
                "size": "50",
                "value": "",
                "step": "any",
                "comparison": attribute.get("comparison"),
                "digits":attribute.get("digits"),
                "label": attribute.get("label")
            }
        )

        # Create a hidden input tag to store the correct answer
        hidden_tag = soup.new_tag(
            name="input",
            attrs={
                "type": "hidden",
                "name": f"{answers_name}_correct",
                "id": f"{answers_name}_correct",
                "value": correct_answer
            }
        )
        
        # Replace the old tag with the new input tag and append the hidden tag
        old_tag.replace_with(new_tag)
        new_tag.insert_after(hidden_tag)
    return soup

def pl_multiple_choice(soup, tag_name, data):
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("The 'soup' argument must be a BeautifulSoup object.")
    
    # Find all old tags that match the provided tag name
    old_tags = soup.find_all(tag_name)
    
    for old_tag in old_tags:
        attributes = old_tag.attrs
        name = attributes.get("answers-name", "")
        choices = old_tag.find_all("choice", recursive=False)

        indices = list(range(len(choices)))
        random.shuffle(indices)
        
        correct_answers = []
        item_order = []
        
        # Create a new div tag to contain the radio buttons
        new_div = soup.new_tag("div", attrs={"class": "multiple-choice-container"})
        
        for idx, original_idx in enumerate(indices):
            choice = choices[original_idx]
            tx = choice.get_text(strip=True)
            id = f"child{original_idx}"
            
            if choice.get('correct') == 'true':
                correct_answers.append(id)
            
            item_order.append(id)
            radio_input = soup.new_tag("input", attrs={
                "type": "radio",
                "name": name,
                "class": "response-mc",
                "id": id,
                "value": idx + 1
            })
            
            # Append the radio button and text to the new div
            new_div.append(radio_input)
            new_div.append(soup.new_string(f" {tx} "))
            new_div.append(soup.new_tag("br"))

        # Replace the old tag with the new div
        old_tag.replace_with(new_div)
        
        # Store the correct answers and item order in data
        data[name] = {
            "correctAnswers": correct_answers,
            "itemOrder": item_order
        }

    return soup

def wrap_input_fields_form(soup):
    """
    Wraps all <input> fields in the given BeautifulSoup object within a <form> tag,
    and adds a submit button at the end.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML to modify.

    Returns:
        BeautifulSoup: The modified BeautifulSoup object with input fields wrapped in a form tag.
    
    Raises:
        TypeError: If the 'soup' argument is not a BeautifulSoup object.
    """
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("The 'soup' argument must be a BeautifulSoup object.")
    
    outer_tag = soup.new_tag(
        name="form",
        attrs={
            "id": "quizForm",
            "class": "answer",
            "method": "POST",
            "action": "/quiz/submit_quiz"
        }
    )
    all_inputs = soup.find_all("input")
    if not all_inputs:
        return soup
    
    first_input = all_inputs[0]
    last_input = all_inputs[-1]
    
    # Insert the new outer tag before the first input tag
    first_input.insert_before(outer_tag)
    
    # Find all elements between the first and last input tags and move them into the new outer tag
    current_element = first_input
    while current_element:
        next_element = current_element.find_next_sibling()
        outer_tag.append(current_element.extract())
        if current_element == last_input:
            break
        current_element = next_element
    
    return soup
    
def wrap_inputs_with_fieldset(soup, name, class_):
    """
    Wraps each <input> field with class 'response' in a <fieldset> tag and its corresponding hidden input.
    Also adds a <label> for each input.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML to modify.

    Returns:
        BeautifulSoup: The modified BeautifulSoup object with input fields wrapped in a fieldset tag.
    
    Raises:
        TypeError: If the 'soup' argument is not a BeautifulSoup object.
    """
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("The 'soup' argument must be a BeautifulSoup object.")
    all_inputs = [soup.find(name=name,class_ = class_)]
    for input_tag in all_inputs:
        print("inside")
        attributes = input_tag.attrs
        fieldset_tag = soup.new_tag(name="fieldset")
        label_tag = soup.new_tag(name="label", attrs={"for": attributes.get("id", "")})
        
        # Set label content
        label_content = attributes.get("label", "")
        label_tag.string = label_content
        # print(label_tag)
        # Find the corresponding hidden input
        correct_input_id = attributes.get("id", "") + "_correct"
        correct_input = soup.find("input", {"id": correct_input_id})
        
        
        # Append the user input and hidden input to the fieldset
        input_tag.wrap(label_tag)
        fieldset_tag.append(label_tag)
        if correct_input:
            fieldset_tag.append(correct_input.extract())
        # Append the fieldset to the form
        soup.form.append(fieldset_tag)
    return soup

def pl_question_panel(soup):
    """
    Wraps the contents of the <pl-question-panel> tag with a <div> element that has the class "question-panel-wrapper".

    Args:
        soup (BeautifulSoup): A BeautifulSoup object containing the HTML to modify.

    Returns:
        BeautifulSoup: The modified BeautifulSoup object.
    
    Raises:
        TypeError: If the 'soup' argument is not a BeautifulSoup object.
    """
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("The 'soup' argument must be a BeautifulSoup object.")
    
    old_tag = soup.find("pl-question-panel")
    if old_tag:
        # Create the new wrapper div
        wrapper = soup.new_tag("div", **{"class": "question-panel-wrapper"})
        
        # Move the contents of the original tag to the new wrapper
        for child in list(old_tag.children):
            wrapper.append(child.extract())
        
        # Replace the original tag with the new wrapper
        old_tag.replace_with(wrapper)
    
    return soup
def pl_figure(soup, qname):
    """
    Creates an <img> tag with attributes derived from the provided tag and question name.

    Args:
        tag (BeautifulSoup.Tag): A BeautifulSoup tag containing attributes.
        qname (str): The question name to construct the image file path.

    Returns:
        BeautifulSoup.Tag: The newly created <img> tag.
    """
    if not isinstance(soup, BeautifulSoup):
        raise TypeError("The 'soup' argument must be a BeautifulSoup object.")
    
    old_tags = soup.find_all("pl-figure")
    for old_tag in old_tags:
        attributes = old_tag.attrs
        file_name = attributes.get('file-name', '')
        im_file_name = f'/questions/{qname}/{file_name}'
        img_tag = soup.new_tag(name ="img", src=im_file_name, alt="Picture for problem", width="300", height="300", class_="pic")
        old_tag.replace_with(img_tag)
    return soup



def process_prairielearn_html(question_html: str, solution_html: str, qdata: dict, qname: str):
    """
    Processes the PrairieLearn HTML by wrapping inputs, adding fieldsets and labels, changing question panels,
    and adding images.

    Args:
        question_html (str): The input HTML string for the question.
        solution_html (str): The input HTML string for the solution.
        qdata (dict): The dictionary containing the question data and additional data for template rendering.
        qname (str): The question name to construct the image file path.

    Returns:
        tuple: The final processed HTML strings for question and solution.

    Raises:
        ValueError: If any processing step fails.
    """
    try:
        soup = BeautifulSoup(question_html, 'html.parser')

        input_processors = {
            "pl-number-input": {
                "oldtag": "pl-number-input",
                "processor": pl_number_input,
                "new_tag": "input",
                "class": "response"
            },
            "pl-multiple-choice": {
                "oldtag": "pl-multiple-choice",
                "processor": pl_multiple_choice,
                "new_tag": "div",
                "class": "multiple-choice-container"
            }
        }

        # Collect all relevant elements and their original positions
        elements = []
        for config in input_processors.values():
            tag = config["oldtag"]
            elements.extend(soup.find_all(tag))

        # Sort elements by their original position in the document
        elements.sort(key=lambda el: (el.sourceline if el.sourceline is not None else float('inf')))

        # Process each element in the sorted order
        for element in elements:
            config = input_processors[element.name]
            processor = config["processor"]
            soup = processor(soup, config["oldtag"], qdata)

        # Adds all the inputs into the main form
        soup = wrap_input_fields_form(soup)

        # Wrap inputs with fieldset and add labels
        for element in elements:
            config = input_processors[element.name]
            new_tag_name = config["new_tag"]
            new_class = config["class"]
            soup = wrap_inputs_with_fieldset(soup, new_tag_name, new_class)

        # Changes question panel
        soup = pl_question_panel(soup)

        # Finds any images
        soup = pl_figure(soup, qname)

        # Adds a submit button
        submit_button = soup.new_tag("input", attrs={"type": "submit", "value": "Submit"})
        if soup.form:
            soup.form.append(submit_button)
        else:
            raise ValueError("No form found in the HTML to append the submit button.")

        html = soup.prettify()

        question_html_template = Template(html).render(qdata)
        print(solution_html)
        solution_html_template = Template(solution_html).render(qdata)

        return question_html_template, solution_html_template

    except Exception as e:
        raise ValueError(f"An error occurred while processing the HTML: {e}")

