import os

from flask import render_template, Blueprint
from flask import session as flask_session
from werkzeug.utils import send_from_directory
from flask import current_app

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def index():
    username = flask_session.get('username')
    return render_template('index.html', username=username)

@static_bp.route('/wifi_pass_map')
def wifi_pass_map():
    return render_template('wifi_pass_map.html')

@static_bp.route('/explore')
def exploremap():
    return render_template('explore.html')

@static_bp.route('/tools')
def tools():
    return render_template('tools.html')

@static_bp.route('/settings')
def settings():
    return render_template('settings.html')

@static_bp.route('/images/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'map_app/static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')