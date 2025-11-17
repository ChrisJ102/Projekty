from flask import Blueprint

errors_bp = Blueprint('errors', __name__)

from movies_api_app.errors import errors
