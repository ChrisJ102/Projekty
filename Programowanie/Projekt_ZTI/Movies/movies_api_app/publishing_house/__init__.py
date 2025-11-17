from flask import Blueprint

publish_house_bp = Blueprint('publishing_house', __name__)

from movies_api_app.publishing_house import publishing_house