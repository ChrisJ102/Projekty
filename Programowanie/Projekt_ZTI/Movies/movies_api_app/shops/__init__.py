from flask import Blueprint

shops_bp = Blueprint('shops', __name__)

from movies_api_app.shops import shops