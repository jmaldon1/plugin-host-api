"""Entry point of the project
"""
import os

from flask import Flask

import settings as _  # Loader script for initializing things.
from conf import config
# from src.logger import logger
from src import utils
from src.api import api_bp


def main():
    """Main function
    Run this file with `python main.py`
    """
    app = Flask(__name__)
    app.secret_key = os.environ['FLASK_SECRET']

    root_dir = os.path.dirname(os.path.abspath(__file__))
    version = utils.slurp(os.path.join(root_dir, "VERSION"))
    route_path = f"/api/{version}"
    app.register_blueprint(api_bp, url_prefix=route_path)

    app.config['CONFIG'] = config

    return app


if __name__ == "__main__":
    flask_app = main()

    host = config['api']['host']
    port = config['api']['port']
    debug = config['api']['debug']
    flask_app.run(debug=debug, host=host, port=port)
