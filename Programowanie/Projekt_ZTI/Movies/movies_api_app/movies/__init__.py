from flask import Blueprint

movies_bp = Blueprint('movies', __name__)

from movies_api_app.movies import movies