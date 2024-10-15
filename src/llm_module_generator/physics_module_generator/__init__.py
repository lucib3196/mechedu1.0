import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# from .module_generator import (
#     question_html_generator,
#     question_solution_generator,
#     server_js_generator,
#     server_py_generator,
# )
