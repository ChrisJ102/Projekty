from flask import Blueprint

category_bp = Blueprint('category', __name__)

from movies_api_app.category import category