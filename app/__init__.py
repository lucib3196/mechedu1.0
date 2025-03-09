from flask import Flask
from flask_login import LoginManager
from flask_wtf import CSRFProtect 
from .config import config




def create_app(config_name):
    app = Flask(__name__)
    # Intialize the configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Protection
    csrf = CSRFProtect(app) 
    csrf.init_app(app)
    
    # Initialize database
    from .db_models.models import db, User,Role
    db.init_app(app)

    # Initialize and configure Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Import and register blueprints
    from .routes.generic_routes.routes import routes
    from .routes.generic_routes.auth import auth
    from .routes.content_generator.text_gen import text_generator_bp
    from .routes.content_generator.image_gen import image_generator_bp
    from .routes.content_generator.lecture_gen import lecture_generator_bp
    from .routes.module_retrieval.module_retrieval import module_retrieval_bp
    from .routes.quiz_views.quiz_overview import quiz_overview_bp
    from .routes.quiz_views.adaptive_questions import adaptive_quiz_bp
    from .routes.quiz_views.nonadaptive_questions import non_adaptive_quiz_bp

    app.register_blueprint(routes, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(module_retrieval_bp, url_prefix="/")
    app.register_blueprint(text_generator_bp, url_prefix="/")
    app.register_blueprint(image_generator_bp, url_prefix="/")
    app.register_blueprint(lecture_generator_bp, url_prefix="/")
    app.register_blueprint(quiz_overview_bp, url_prefix="/")
    app.register_blueprint(adaptive_quiz_bp, url_prefix="/")
    app.register_blueprint(non_adaptive_quiz_bp, url_prefix="/")

    # Create database tables
    with app.app_context():
        db.create_all()
        Role.insert_roles()


    return app
