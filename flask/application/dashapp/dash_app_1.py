import dash
from flask import current_app
from flask.helpers import get_root_path
import dash_bootstrap_components as dbc


def add_dash(server):
    from .layout import render_layout
    from .callbacks import register_callbacks

    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets = [
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
        dbc.themes.FLATLY
    ]
    app = dash.Dash(
        server=server,
        external_stylesheets=external_stylesheets,
        routes_pathname_prefix='/' + current_app.config.get('DASH_URL_BASE'),
        requests_pathname_prefix=(current_app.config.get('APPLICATION_ROOT') + '/dash/dash_app_1/').replace('//', '/'),
        assets_folder=get_root_path(__name__) + '/assets/',
        meta_tags=[meta_viewport],
        suppress_callback_exceptions=True
    )
    app.layout = render_layout
    register_callbacks(app)
    return server
