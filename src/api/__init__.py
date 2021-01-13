"""Api blueprint
"""
from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import at bottom to avoid circular imports
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxiii-application-programming-interfaces-apis
# pylint: disable=wrong-import-position
from src.api.routes import proxy
