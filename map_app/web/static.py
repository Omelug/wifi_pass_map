import os

from flask import render_template, Blueprint, render_template_string
from flask import session as flask_session
from werkzeug.utils import send_from_directory
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

@static_bp.route('/explore')
def exploremap():
    return render_template('explore.html')

@static_bp.route('/tools')
def tools():
    buttons_html = ""
    for tool in tool_management.tool_list().keys():
        tool_name = os.path.splitext(tool)[0]
        buttons_html += f'''
        <div class="button-container">
            <button id="{tool_name}_button" onclick="runTool('{tool_name}')">{tool_name.upper()}</button>
            <div id="{tool_name}_result" class="result"></div>
        </div>
        '''

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tools</title>
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/menu.css') }}">
        <link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/tools.css') }}">
        <link rel="icon" href="{{ url_for('static', filename='images/favicon.ico') }}">
    </head>
    <body>
        {{ buttons_html|safe }}
        <div class="result-container">
            <div id="live-results" class="result-text"></div>
        </div>
        <button class="clear-button" onclick="clearOutput()">Clear Output</button>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="{{ url_for('static', filename='js/tools.js') }}"></script>
    </body>
    </html>
    ''', buttons_html=buttons_html)

@static_bp.route('/images/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'map_app/static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')