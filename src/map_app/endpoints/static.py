import os
from flask import render_template, Blueprint, Response
from flask import session as flask_session
from flask import send_from_directory
from flask import current_app

from map_app.source_core.manager import tool_list

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def index() -> str:
    username = flask_session.get('username')
    return render_template('index.html', username=username)

@static_bp.route('/wifi_pass_map')
def wifi_pass_map() -> str:
    return render_template('wifi_pass_map.html')

@static_bp.route('/tools')
def tools() -> str:
    return render_template('tools.html', tools=tool_list())


# --------------GENERIC --------------------------
@static_bp.route('/images/<path:filename>')
def serve_image(filename) -> Response:
    return send_from_directory(os.path.join(current_app.root_path, 'map_app/static'), filename)
