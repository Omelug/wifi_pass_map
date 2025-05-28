from flask import Flask
from .endpoints.static import static_bp
from .endpoints.api import api_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(api_bp)
    app.register_blueprint(static_bp)

    return app
