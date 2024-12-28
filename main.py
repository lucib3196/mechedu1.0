from app import create_app
import os
from dotenv import load_dotenv
load_dotenv()
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    print(" Starting app...")
    print(f"Running {os.getenv('FLASK_CONFIG')}")
    app.run(debug=True)