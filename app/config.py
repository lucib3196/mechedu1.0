import os 
from dotenv import load_dotenv
load_dotenv()
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
print(f"Base Directory: {basedir}")

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN', "").split(",")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    @staticmethod
    def init_app(app):
        pass
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///files.db"
class ProductionConfig(Config): 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
config: dict[str, type[Config]] = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


