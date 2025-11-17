from flask import Blueprint

loans_bp = Blueprint('loans', __name__)

from movies_api_app.loans import loans