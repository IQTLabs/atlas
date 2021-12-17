from flask import Flask
from config import BaseConfig


def create_app():
    server = Flask(__name__)
    server.static_url_path = (BaseConfig.APPLICATION_ROOT + '/static').replace('//', '/')
    server.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

    # NOTE: APPLICATION_ROOT is set in the line below. defaults to '/'
    server.config.from_object(BaseConfig)

    register_dashapps(server)
    register_blueprints(server)

    return server


def register_dashapps(app):
    with app.app_context():
        # process dash app

        # dash app 1
        from .dashapp.dash_app_1 import add_dash as ad1
        request_ctx = app.test_request_context()
        request_ctx.push()
        ad1(app)


def register_blueprints(server):
    from .routes import server_bp
    from .dashapp.routes import dashapp_bp

    server.register_blueprint(server_bp)
    server.register_blueprint(dashapp_bp)
