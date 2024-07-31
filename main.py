from app import create_app

app = create_app()
#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    print(" Starting app...")
    app.run(debug=True)