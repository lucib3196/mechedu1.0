from flask import Flask
from .db_models.models import db
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

def create_app():
    app = Flask(__name__)
    Bootstrap(app)
    app.config["SECRET_KEY"] = "sgjiksbnergksebngrksegjnbser"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///files.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # Initialize the database with the app
    db.init_app(app)

    # Import and register blueprints
    from .routes.generic_routes.routes import routes
    from .routes.content_generator.text_gen import text_generator_bp
    from .routes.content_generator.image_gen import image_generator_bp
    from .routes.content_generator.lecture_gen import lecture_generator_bp
    from .routes.module_retrieval.module_retrieval import module_retrieval_bp
    from .routes.quiz_views.quiz_overview import quiz_overview_bp
    from .routes.quiz_views.adaptive_questions import adaptive_quiz_bp
    # from .quiz_generator import quiz_generator
    # from .file_management import file_management
    # from .generator_routes.generate_from_text import text_generator_bp
    # from .generator_routes.generate_from_image import image_generator_bp
    # from .generator_routes.generate_from_lecture import lecture_generator_bp
    # from .modules_routes.view_modules import view_modules_bp

    app.register_blueprint(routes, url_prefix="/")
    app.register_blueprint(module_retrieval_bp, url_prefix="/")
    app.register_blueprint(text_generator_bp, url_prefix="/")
    app.register_blueprint(image_generator_bp, url_prefix="/")
    app.register_blueprint(lecture_generator_bp, url_prefix="/")
    app.register_blueprint(quiz_overview_bp)
    app.register_blueprint(adaptive_quiz_bp)



    # app.register_blueprint(quiz_generator, url_prefix="/")
    # app.register_blueprint(file_management,url_prefix="/")
    # app.register_blueprint(text_generator_bp,url_prefix="/")
    # app.register_blueprint(image_generator_bp,url_prefix="/")
    # app.register_blueprint(lecture_generator_bp,url_prefix="/")
    # app.register_blueprint(view_modules_bp,url_prefix="/")
    
    
    # Create database tables
    with app.app_context():
        db.create_all()

    return app
