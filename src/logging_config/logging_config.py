import logging

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s - %(lineno)d]",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()          # Log to console
    ]
)
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
def get_logger(name):
    return logging.getLogger(name)
