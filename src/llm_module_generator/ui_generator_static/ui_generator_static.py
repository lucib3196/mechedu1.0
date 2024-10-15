from bs4 import BeautifulSoup
from . import extract_summary,extract_derivations,extract_conceptual_questions
import asyncio
import os
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_openai import OpenAI
from langchain.agents import initialize_agent, Tool, AgentType
import pprint


def lecture_summary_parser(response: dict, search: bool = False) -> tuple[str, str]:
    # Create BeautifulSoup objects for the lecture and search content
    lecture_soup = BeautifulSoup("", "html.parser")
    search_soup = BeautifulSoup("", "html.parser")

    # Extract the analysis data from the dictionary
    analysis = response['analysis']

    # Title and subtitle section for lecture content
    title_section = lecture_soup.new_tag('section', **{'class': 'title_section'})
    title = lecture_soup.new_tag("h1", **{'class': 'title'})
    subtitle = lecture_soup.new_tag("h3", **{'class': 'subtitle'})

    title.string = analysis.get('lecture_name', 'Untitled Lecture')
    subtitle.string = analysis.get('lecture_subtitle', 'A detailed discussion on the lecture content')

    title_section.append(title)
    title_section.append(subtitle)
    lecture_soup.append(title_section)

    # Summary section for lecture content
    summary_section = lecture_soup.new_tag('section', **{'class': 'summary_section'})
    summary_header = lecture_soup.new_tag('h2')
    summary_header.string = "Lecture Summary"
    summary_intro = lecture_soup.new_tag('p')
    summary_intro.string = "Below is a brief summary of the core content covered in this lecture."

    summary_content = lecture_soup.new_tag('p', **{'class': 'summary'})
    summary_content.string = analysis['summary']

    summary_section.append(summary_header)
    summary_section.append(summary_intro)
    summary_section.append(summary_content)
    lecture_soup.append(summary_section)

    # Key Concepts section for lecture content
    key_concepts_section = lecture_soup.new_tag('section', **{'class': 'key_concepts_section'})
    key_concepts_header = lecture_soup.new_tag('h2')
    key_concepts_header.string = "Key Concepts"
    key_concepts_intro = lecture_soup.new_tag('p')
    key_concepts_intro.string = "These are the most important concepts covered in the lecture, including key definitions and relevant formulas."

    key_concepts_ul = lecture_soup.new_tag("ul", **{'class': 'key_concepts_list'})
    for key_concept in analysis['key_concepts']:
        li_tag = lecture_soup.new_tag('li')

        concept = key_concept.get("keyword", "")
        description = key_concept.get("description", "")
        
        keyword_span = lecture_soup.new_tag('span', **{'class': 'bold'})
        keyword_span.string = concept
        li_tag.append(keyword_span)
        if description:
            li_tag.append(": " + description)
        key_concepts_ul.append(li_tag)

    key_concepts_section.append(key_concepts_header)
    key_concepts_section.append(key_concepts_intro)
    key_concepts_section.append(key_concepts_ul)
    lecture_soup.append(key_concepts_section)

    # Foundational Concepts section for lecture content
    foundational_concepts_section = lecture_soup.new_tag('section', **{'class': 'foundational_concepts_section'})
    foundational_concepts_header = lecture_soup.new_tag('h2')
    foundational_concepts_header.string = "Foundational Concepts"
    foundational_concepts_intro = lecture_soup.new_tag('p')
    foundational_concepts_intro.string = "These are the foundational ideas and prior knowledge that this lecture builds upon."

    foundational_concepts_ul = lecture_soup.new_tag("ul", **{'class': 'foundational_concepts_list'})
    for f_concept in analysis['foundational_concepts']:
        li_tag = lecture_soup.new_tag('li')

        concept = f_concept.get("keyword", "")
        description = f_concept.get("description", "")
        
        keyword_span = lecture_soup.new_tag('span', **{'class': 'bold'})
        keyword_span.string = concept
        li_tag.append(keyword_span)
        if description:
            li_tag.append(": " + description)
        foundational_concepts_ul.append(li_tag)

    foundational_concepts_section.append(foundational_concepts_header)
    foundational_concepts_section.append(foundational_concepts_intro)
    foundational_concepts_section.append(foundational_concepts_ul)
    lecture_soup.append(foundational_concepts_section)

    # Search results section, if enabled
    if search:
        search_api = GoogleSerperAPIWrapper(k=1)
        search_section = search_soup.new_tag('section', **{'class': 'search_keywords_section'})
        
        # Header for the section
        search_header = search_soup.new_tag('h2')
        search_header.string = "Additional Resources for Further Study"
        search_section.append(search_header)
        
        # Introductory paragraph for the section
        search_intro = search_soup.new_tag('p')
        search_intro.string = "The following are additional resources that may be useful for further exploring the lecture material:"
        search_section.append(search_intro)

        # List for search results
        search_keywords_ul = search_soup.new_tag("ul", **{'class': 'search_keywords_list'})
        
        # Iterate through search keywords
        for search_keyword in analysis.get('search_keywords', []):
            results = search_api.results(search_keyword)
            organic = results.get('organic', [])
            
            if organic:  # Ensure we have at least one organic result
                # Only using the first organic result
                first_result = organic[0]
                title = first_result.get("title", "No title available")
                link = first_result.get('link', '#')  # Default to # if no link available

                # Create a list item for each result
                li_tag = search_soup.new_tag('li')
                
                # Create the link
                a_tag = search_soup.new_tag('a', href=link, target="_blank")  # Open in a new tab
                a_tag.string = title

                # Append the link to the list item
                li_tag.append(a_tag)
                search_keywords_ul.append(li_tag)

        # Append the search results list to the search section
        search_section.append(search_keywords_ul)
        search_soup.append(search_section)

    # Return the prettified HTML for both lecture and search content
    return lecture_soup.prettify(), search_soup.prettify() if search else None # type: ignore


def derivation_parser(response: dict) -> str:
    # Create a BeautifulSoup object for the derivation content
    derivation_soup = BeautifulSoup("", "html.parser")

    # Create a wrapper for all derivations
    derivations_section = derivation_soup.new_tag('section', **{'class': 'derivations_section'})

    # Iterate over each derivation in the response
    for derivation in response.get('derivations', []):
        # Derivation section
        derivation_section = derivation_soup.new_tag('div', **{'class': 'derivation_container'})
        
        # Derivation name as a header
        derivation_name = derivation_soup.new_tag('h2', **{'class': 'derivation_name'})
        derivation_name.string = derivation.get("derivation_name", "Unnamed Derivation")
        derivation_section.append(derivation_name)

        # Derivation source
        derivation_source_p = derivation_soup.new_tag('p', **{'class': 'derivation_source'})
        derivation_source_p.string = f"Source: {derivation.get('derivation_source', 'Unknown Source')}"
        derivation_section.append(derivation_source_p)

        # Derivation steps
        steps_header = derivation_soup.new_tag('h3')
        steps_header.string = "Derivation Steps"
        derivation_section.append(steps_header)

        steps_ol = derivation_soup.new_tag('ol', **{'class': 'derivation_steps'})
        for step in derivation.get("derivation_steps", []):
            li_tag = derivation_soup.new_tag('li')
            # Each step should be formatted using LaTeX (assumed to be included in the step's description)
            li_tag.string = step.get("step_description", "No description available")  
            steps_ol.append(li_tag)

        derivation_section.append(steps_ol)

        # Image requirements, if any
        image_stats = derivation.get("image_stats", [])
        if image_stats:
            image_requirements_header = derivation_soup.new_tag('h3')
            image_requirements_header.string = "Image Requirements"
            derivation_section.append(image_requirements_header)

            image_requirements_ul = derivation_soup.new_tag('ul', **{'class': 'image_requirements'})
            for image_requirement in image_stats:
                li_tag = derivation_soup.new_tag('li')
                requires_image = image_requirement.get("requires_image", "False")
                recommended_image = image_requirement.get("recommended_image", "No recommendation")
                li_tag.string = f"Requires Image: {requires_image}. Recommended: {recommended_image}"
                image_requirements_ul.append(li_tag)

            derivation_section.append(image_requirements_ul)

        # Append the derivation section to the derivations_section
        derivations_section.append(derivation_section)

    # Append the entire derivations section to the main soup
    derivation_soup.append(derivations_section)

    # Return the prettified HTML
    return derivation_soup.prettify()

from bs4 import BeautifulSoup
from typing import List

def conceptual_questions_parser(response: dict) -> str:
    # Create a BeautifulSoup object for the conceptual questions
    questions_soup = BeautifulSoup("", "html.parser")

    # Create a wrapper for all questions
    questions_section = questions_soup.new_tag('section', **{'class': 'questions_section'})

    # Iterate over each question in the response
    for question_data in response.get('questions', []):
        # Question section
        question_section = questions_soup.new_tag('div', **{'class': 'question_container'})
        
        # Add the question as a header
        question_header = questions_soup.new_tag('h3', **{'class': 'question'})
        question_header.string = question_data.get("question", "No question available")
        question_section.append(question_header)

        # Add the multiple-choice options
        options_header = questions_soup.new_tag('h4')
        options_header.string = "Multiple Choice Options"
        question_section.append(options_header)

        options_ol = questions_soup.new_tag('ol', **{'class': 'multiple_choice_options'})
        for option in question_data.get("multiple_choice_options", []):
            li_tag = questions_soup.new_tag('li')
            li_tag.string = option
            options_ol.append(li_tag)

        question_section.append(options_ol)

        # Add the correct answer
        data_container = questions_soup.new_tag('div', **{'class': 'data_container'})
        correct_answer_p = questions_soup.new_tag('p', **{'class': 'correct_answer'})
        correct_answer_p.string = f"Correct Answer: {question_data.get('correct_answer', 'No answer available')}"
        

        # Add the source
        source_p = questions_soup.new_tag('p', **{'class': 'source'})
        source_p.string = f"Source: {question_data.get('source', 'Unknown source')}"
        

        # Add if the question was generated or extracted
        generated_p = questions_soup.new_tag('p', **{'class': 'generated'})
        generated = question_data.get("generated", False)
        generated_p.string = f"Generated: {'Yes' if generated else 'No'}"


        data_container.append(correct_answer_p)
        data_container.append(source_p)
        data_container.append(generated_p)

        button= questions_soup.new_tag("button", type="button", **{'class': 'btn btn-primary'})
        button.string = "Reveal Answer"    

        question_section.append(data_container)   
        question_section.append(button)   
        # Append the question section to the main questions section
        questions_section.append(question_section)


    # Append the entire questions section to the main soup
    questions_soup.append(questions_section)

    # Return the prettified HTML
    return questions_soup.prettify()


async def generate_conceputal_html_static(image_paths:list[str]):
    # Send the request for conceptual questions
    conc_res = await extract_conceptual_questions.send_request(image_paths)
    # Parse the response and return the HTML
    return conceptual_questions_parser(conc_res)  # Returns HTML
async def generate_derivation_html_static(image_paths:list[str]):
    # Send the request for derivations
    der_res = await extract_derivations.send_request(image_paths)
    # Parse the response and return the HTML
    return derivation_parser(der_res)  # Returns HTML

async def generate_lecture_html_static(image_paths:list[str],search:bool=False):
    # Send the request for the lecture summary
    sum_res = await extract_summary.send_request(image_paths)
    # Parse the response and return the HTML
    return lecture_summary_parser(sum_res,search = False)  # Returns html needs to be handled just incase of search


async def process_image_paths(image_paths):
    # Run all functions concurrently
    conc_html, der_html, sum_html = await asyncio.gather(
        generate_conceputal_html_static(image_paths),
        generate_derivation_html_static(image_paths),
        generate_lecture_html_static(image_paths)
    )

    # Return the HTML results
    results = [ conc_html, der_html, sum_html]
    return results


async def main():
    image_paths = [
        r"C:\Users\lberm\OneDrive\Documents\Github\mechedu1.0\test_images\mass_block.png"
    ]
    results = await process_image_paths(image_paths)
    for result in results:
        print(f"\nResult\n: {result}")

if __name__ == "__main__":
    asyncio.run(main())