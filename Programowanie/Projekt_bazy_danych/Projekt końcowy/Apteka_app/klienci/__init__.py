from flask import Blueprint

klienci_bp = Blueprint('klienci', __name__)

from Apteka_app.klienci import klienci