from flask import Blueprint

moviesinship_bp = Blueprint('moviesinshop', __name__)

from movies_api_app.moviesinshop import moviesinshop