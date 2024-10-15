from fastapi import FastAPI
from langserve import add_routes
# Initialize the FastAPI app
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the environment variables
langchain_tracing = os.getenv("LANGCHAIN_TRACING_V2")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
project_name =os.getenv("project_name")
server_key = os.getenv("SERPER_API_KEY")