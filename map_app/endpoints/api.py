import configparser
import logging
import os
from flask import jsonify, request, Response, stream_with_context, Blueprint
from map_app import sources

api_bp = Blueprint('api', __name__)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

POT_UPLOAD_FOLDER = 'app/data/potfile'
ALLOWED_EXTENSIONS = {'pot', '22000', 'potfile'}

# ------------MAPS--------------
@api_bp.route('/api/wifi_pass_map')
def pwnapi():
    """Load first data to map"""
    log.debug(f"Request Path: {request.path} was called")

    pwned_data,script_statuses = sources.get_AP_data()
    return jsonify({
        'data': pwned_data,
        'script_statuses': script_statuses,
        'AP_len': len(pwned_data)
    })

@api_bp.route('/api/explore')
def exploreapi():
    log.debug(f"Request Path: {request.path} was called")

    # Extract filters from request parameters, if not None
    filters = {key: value for key, value in {
        'essid': request.args.get('name'),
        'bssid': request.args.get('network_id'),
        'limit': request.args.get('limit'),
        'encryption': request.args.get('encryption'),
        'network_type': request.args.get('network_type'),
        #'exclude_no_ssid': request.args.get('exclude_no_ssid', 'false')
    }.items() if value is not None}

    pwned_data, script_statuses = sources.get_AP_data(filters=filters)
    return jsonify({
        'data': pwned_data,
        'script_statuses': script_statuses,
        'AP_len': len(pwned_data)
    })


@api_bp.route('/api/load_sqare')
def load_sqare():
    log.debug(f"Request Path: {request.path} was called")

    # Extract params from request parameters
    filters = {key: value for key, value in {
        'center_latitude': request.args.get('center_latitude'),
        'center_longitude': request.args.get('center_longitude'),
        'sqare_limit': request.args.get('sqare_limit'),
    }.items() if value is not None}

    pwned_data, script_statuses = sources.get_AP_data(filters)
    return jsonify({
        'data': pwned_data,
        'script_statuses': script_statuses,
        'AP_len': len(pwned_data)
    })


# ------------TOOLS--------------
@api_bp.route('/api/tools', methods=['POST'])
def run_script():
    tools = sources.tool_list()
    # Get script name and optional arguments from the POST request
    script_name = request.json.get('script_name')
    tool_name = request.json.get('tool_name')

    if not script_name or not tool_name:
        log.warning(f"Request Path: {request.path} - Script name or tool name not provided")
        return {"status": "error", "message": "Script name or tool name not provided."}, 400

    if script_name not in tools.keys():
        log.error(f"Request Path: {request.path} - The script {script_name} was not found")
        return {"status": "error", "message": f"Script not found, available options are {', '.join(tools.keys())}"}, 404

    if tool_name not in tools[script_name].keys():
        log.error(f"Request Path: {request.path} - The tool {tool_name} was not found in script {script_name}")
        return {"status": "error", "message": f"Tool not found in script {script_name}"}, 404

    def generate_output(func):
        from io import StringIO
        import sys

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            func()
            mystdout.seek(0)
            for line in mystdout:
                yield line
        finally:
            sys.stdout = old_stdout

    func = tools[script_name][tool_name]["run_fun"]
    return Response(stream_with_context(generate_output(func)), content_type='text/plain')

@api_bp.route('/api/save_params', methods=['POST'])
def save_params():
    data = request.json
    script_name = data.get('script_name')
    tool_name = data.get('tool_name')
    params = data.get('params')

    if not script_name or not tool_name or not params:
        return {"status": "error", "message": "Script name or tool name or parameters missing"}, 400

    config_file = os.path.join(os.path.dirname(__file__), '..', 'sources', f'config/{script_name}.ini')
    config = configparser.ConfigParser()

    if os.path.exists(config_file):
        config.read(config_file)
    else:
        return {"status": "error", "message": f"Config file for {script_name} not found"}, 404


    # Update the tool section with the new parameters
    if tool_name not in config:
        config[tool_name] = {}

    for param_name, param_value in params.items():
        #TODO check param control function from tools list
        config[tool_name][param_name] = str(param_value)

    with open(config_file, 'w') as cf:
        config.write(cf)

    return {"status": "success", "message": "Parameters saved successfully"}, 200
