import sys
import os
import lxml.html

# Define the path to the 'src' directory where 'prairielearn' is located
src_dir = os.path.join(os.getcwd(), 'src')

# Add 'src' to sys.path if it's not already present
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Try to import the 'prairielearn' module
try:
    from prairielearn.python import prairielearn as pl
except ImportError as e:
    print(f"Error importing prairielearn module: {e}")


def prepare(element_html: str, data: pl.QuestionData) -> None:
    element = lxml.html.fragment_fromstring(element_html)
    pl.check_attribs(element, required_attribs=[], optional_attribs=[])


def render(element_html: str, data: pl.QuestionData) -> str:
    if data["panel"] == "answer":
        element = lxml.html.fragment_fromstring(element_html)
        return pl.inner_html(element)

    return ""
