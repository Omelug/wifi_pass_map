import os
from flask import render_template, Blueprint
from flask import session as flask_session
from flask import send_from_directory
from flask import current_app
import map_app.tools.tool_management as tool_management

static_bp = Blueprint('static', __name__)

@static_bp.route('/')
def index():
    username = flask_session.get('username')
    return render_template('index.html', username=username)

@static_bp.route('/wifi_pass_map')
def wifi_pass_map():
    return render_template('wifi_pass_map.html')

@static_bp.route('/tools')
def tools():
    tool_data = tool_management.tool_list()
    return render_template('tools.html', tools=tool_data)

@static_bp.route('/images/<path:filename>')
def serve_image(filename):
    print(filename)
    return send_from_directory(os.path.join(current_app.root_path, 'map_app/static'), filename)