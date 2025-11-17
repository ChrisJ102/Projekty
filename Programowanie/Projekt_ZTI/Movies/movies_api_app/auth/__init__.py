from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from movies_api_app.auth import auth, tasks
