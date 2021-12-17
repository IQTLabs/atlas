from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.flaskenv'))

class BaseConfig:
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ['FLASK_ENV']
    FLASK_DEBUG = environ['FLASK_DEBUG']
    HASURA_GRAPHQL_ADMIN_SECRET = environ['HASURA_GRAPHQL_ADMIN_SECRET']
    HASURA_GRAPHQL_API = environ['HASURA_GRAPHQL_API']
    CLIENT_HASURA_GRAPHQL_API = environ['CLIENT_HASURA_GRAPHQL_API']
    UPLOAD_EXTENSIONS = ['.json']
    DASH_URL_BASE = 'dash/dash_app_1/'
    SECRET_KEY = environ['SECRET_KEY']
    # Set APPLICATION_ROOT when deploying Flask app to a subdirectory
    APPLICATION_ROOT = environ.get('APPLICATION_ROOT', '/')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024