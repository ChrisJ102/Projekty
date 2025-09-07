from flask import Blueprint

transakcja_bp = Blueprint('transakcja', __name__)

from Apteka_app.transakcja import transakcja