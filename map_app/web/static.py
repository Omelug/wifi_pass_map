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
    buttons_html = ""
    for script_name, tool_info in tool_management.tool_list().items():
        script_name = os.path.splitext(script_name)[0]
        for tool_name, tool_details in tool_info.items():
            buttons_html += f'''
                <div class="tool-container">
                    <button id="{script_name}_{tool_name}_button" onclick="runTool('{script_name}', '{tool_name}')">{tool_name.upper()}</button>
                    <button id="{script_name}_{tool_name}_save_button" class="save-button" onclick="saveParams('{script_name}', '{tool_name}')">S</button>
                    <div id="{script_name}_{tool_name}_result" class="result"></div>
                </div>
            '''

            if "params" in tool_details:
                for param_name, param_type, param_control, param_old_value, param_desc in tool_details["params"]:
                    buttons_html += f'''
                      <div class="input-container">
                          <label for="{script_name}_{tool_name}_{param_name}"> {param_type.__name__} | {param_name}</label>
                          <input type="text" id="{script_name}_{tool_name}_{param_name}" name="{param_name}" value="{param_old_value}">
                          <label>{param_desc}</label>
                      </div>
                      '''

    return render_template('tools.html', buttons_html=buttons_html)

@static_bp.route('/images/<path:filename>')
def serve_image(filename):
    print(filename)
    return send_from_directory(os.path.join(current_app.root_path, 'map_app/static'), filename)