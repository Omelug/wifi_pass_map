from flask import Flask
from .endpoints.static import static_bp
from .endpoints.api import api_bp

def create_app():
    app = Flask(
        __name__,
        static_folder='static',
        static_url_path='/static'
    )

    print("Flask static folder:", app.static_folder)

    app.register_blueprint(api_bp)
    app.register_blueprint(static_bp)

    return app
