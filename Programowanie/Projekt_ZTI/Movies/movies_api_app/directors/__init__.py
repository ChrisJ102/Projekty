from flask import Blueprint

directors_bp = Blueprint('directors', __name__)

from movies_api_app.directors import directors