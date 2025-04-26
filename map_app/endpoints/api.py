import configparser
import logging
import os
import sys
from io import StringIO

from flask import jsonify, request, Response, stream_with_context, Blueprint

from formator.files import source_object_name
from map_app import sources

api_bp = Blueprint('api', __name__)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

SAFE_CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config"))


# ------------MAPS--------------
@api_bp.route('/api/wifi_pass_map')
def pwnapi():
    """Load first data to map"""
    log.debug(f"Request Path: {request.path} was called")
    pwned_data,script_statuses = sources.get_AP_data()
    return jsonify({'data': pwned_data,'script_statuses': script_statuses,'AP_len': len(pwned_data)})

@api_bp.route('/api/explore')
def exploreapi():
    """Load filtered AP data"""
    log.debug(f"Request Path: {request.path} was called")

    filters = {k:v for k,v in {
        'essid': request.args.get('name'),
        'bssid': request.args.get('network_id'),
        'limit': request.args.get('limit'),
        'encryption': request.args.get('encryption'),
        'network_type': request.args.get('network_type'),
    }.items() if v is not None}

    ap_data, script_statuses = sources.get_AP_data(filters=filters)
    return jsonify({'data': ap_data, 'script_statuses': script_statuses, 'AP_len': len(ap_data) })


@api_bp.route('/api/load_sqare', methods=["POST"])
def load_sqare():
    log.debug(f"Request Path: {request.path} was called")

    filters = {k: v for k, v in {
        "center_latitude": request.args.get("center_latitude"),
        "center_longitude": request.args.get("center_longitude"),
        "square_limit": request.args.get("square_limit"),
    }.items() if v is not None}

    ap_data, script_statuses = sources.get_AP_data(filters)
    return jsonify({'data': ap_data,'script_statuses': script_statuses,'AP_len': len(ap_data)})


# ------------TOOLS--------------
@api_bp.route('/api/tools', methods=['POST'])
def run_tool():
    """Run specified tool script, stream its output."""
    tools = sources.tool_list(add_class=True)

    # Get script name and optional arguments from the POST request
    object_name = request.json.get('object_name')
    tool_name = request.json.get('tool_name')

    if not object_name or not tool_name:
        log.warning(f"Request Path: {request.path} - Script name or tool name not provided")
        return {"status": "error", "message": "Script name or tool name not provided."}, 400

    if object_name not in tools.keys():
        log.error(f"Request Path: {request.path} - The script {object_name} was not found")
        return {"status": "error", "message": f"Script not found, available options are {', '.join(tools.keys())}"}, 404

    if tool_name not in tools[object_name].keys():
        log.error(f"Request Path: {request.path} - The tool {tool_name} was not found in script {object_name}")
        return {"status": "error", "message": f"Tool not found in script {object_name}"}, 404

    def generate_output(func):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            func()
            mystdout.seek(0)
            for line in mystdout:
                yield line
        finally:
            sys.stdout = old_stdout

    print(tools[object_name][tool_name])
    func = tools[object_name][tool_name]["run_fun"]
    return Response(stream_with_context(generate_output(func)), content_type='text/plain')

@api_bp.route('/api/save_params', methods=['POST'])
def save_params():
    """Save user-defined parameters for a given source script and tool."""
    data = request.json or {}
    object_name = data.get('object_name')
    tool_name = data.get('tool_name')
    params = data.get('params')

    if not object_name or not tool_name or not params:
        return {"status": "error", "message": "Script name or tool name or parameters missing"}, 400

    #secure input
    config_file = os.path.join(SAFE_CONFIG_DIR, f"{object_name}.ini")
    if not config_file.startswith(SAFE_CONFIG_DIR) or not source_object_name(object_name):
        return {"status": "error", "message": "Invalid script name."}, 400

    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        return {"status": "error", "message": f"Config file for {object_name} not found"}, 404

    if tool_name not in config:
        config[tool_name] = {}

    for param_name, param_value in params.items():
        config[tool_name][param_name] = str(param_value)

    with open(config_file, 'w') as cf:
        config.write(cf)

    return {"status": "success", "message": "Parameters saved successfully"}, 200
