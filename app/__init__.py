from flask import Flask
from os import path

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sgjiksbnergksebngrksegjnbser"
    
    from .routes import routes
    from .quiz_generator import quiz_generator
    
    app.register_blueprint(routes,url_prefix = "/")
    app.register_blueprint(quiz_generator,url_prefix = "/")
    
    return app
    
    
    