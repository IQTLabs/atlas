from flask import Blueprint

dashapp_bp = Blueprint(
    'dashapp_bp', __name__,
    template_folder='templates',
    static_folder='static'
)
