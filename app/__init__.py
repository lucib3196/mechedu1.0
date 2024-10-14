import os
from flask import Flask
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from pickle import TRUE
from src.prairielearn.python import prairielearn
from src.prairielearn.python import prairielearn as pl
import json
from flask_wtf import CSRFProtect 


class Config:
    SECRET_KEY = "6Vicv382oz3PyNOAYP2SlAo/uO2750TY4+5fjNRoi8ccH0fpoEP/QLznbI07K36v"
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN', "").split(",")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///files.db"

config: dict[str, type[DevelopmentConfig]] = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}

def create_app():
    app = Flask(__name__)
    app.config.from_object(config['development'])

    csrf = CSRFProtect(app) 
    csrf.init_app(app)

    # Initialize database
    from .db_models.models import db, User,Role,QuestionMetadata,Folder
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

        # folder = Folder.query.filter_by(name='Example Folder').first()
        # if folder is None:
        #     folder = Folder(name='Example Folder', module_id=1)  # Assuming module_id=1 exists
        #     db.session.add(folder)
        #     db.session.commit()

        # question = QuestionMetadata(
        # uuid="d8b914d1-5f8e-4e44-994f-e78e08d396f1",
        # title="ProjectileMotionCalculation",
        # stem="Calculating the time taken for an object to fall from a height",
        # topic="Physics",
        # tags=json.dumps(["Projectile Motion", "Physics", "Kinematics", "Free Fall"]),
        # prereqs=json.dumps(["Basic understanding of kinematics", "Knowledge of free fall motion"]),
        # is_adaptive=True,
        # created_by="lberm007@ucr.edu",
        # q_type="num",
        # n_steps=1,
        # updated_by="",
        # difficulty=1,
        # codelang="javascript",
        # reviewed=False,
        # folder_id=folder.id)
        # db.session.add(question)
        # db.session.commit()

    return app
