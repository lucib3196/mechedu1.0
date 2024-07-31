import os
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

# Load the API key from an environment variable
api_key = os.environ.get('OPENAI_API_KEY')

if not api_key:
    raise ValueError("No API key found. Set the API_KEY environment variable.")