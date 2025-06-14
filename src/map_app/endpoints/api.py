import configparser
import json
import logging
import os
import threading
import queue
from typing import Any, Dict, Tuple

from flask import jsonify, request, Response, Blueprint

from formator.files import source_object_name
from map_app.source_core import manager
from map_app.source_core.GlobalConfig import GlobalConfig
from map_app.source_core.manager import get_AP_data, tool_list

api_bp = Blueprint('api', __name__)

SAFE_CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..","sources","config"))

# ------------MAPS--------------
@api_bp.route('/api/wifi_pass_map')
def pwnapi()->Response:
    """Load first data to map"""
    logging.debug(f"Request Path: {request.path} was called")
    pwned_data,script_statuses = get_AP_data()
    return jsonify({'data': pwned_data,'script_statuses': script_statuses,'AP_len': len(pwned_data)})

@api_bp.route('/api/search')
def searchapi() -> Response:
    """Load filtered AP data"""
    logging.debug(f"Request Path: {request.path} was called")

    filters = {k: v for k, v in {
        'essid': request.args.get('name'),
        'bssid': request.args.get('bssid'),
        'limit': request.args.get('limit'),
        'encryption': request.args.get('encryption'),
        'network_type': request.args.get('network_type'),
        'regex': request.args.get('regex')
    }.items() if v not in (None, '')}

    ap_data, script_statuses = get_AP_data(filters=filters)
    return jsonify({'data': ap_data, 'script_statuses': script_statuses, 'AP_len': len(ap_data) })


@api_bp.route('/api/load_sqare', methods=["POST"])
def load_sqare() -> Response:
    logging.debug(f"Request Path: {request.path} was called")

    filters = {k: v for k, v in {
        "center_latitude": request.args.get("center_latitude"),
        "center_longitude": request.args.get("center_longitude"),
        "square_limit": request.args.get("square_limit"),
    }.items() if v is not None}

    ap_data, script_statuses = get_AP_data(filters)
    return jsonify({'data': ap_data,'script_statuses': script_statuses,'AP_len': len(ap_data)})

# ------------TOOLS--------------
@api_bp.route('/api/tools', methods=['POST'])
def run_tool() -> Tuple[Dict[str, Any], int] | Response:
    """Run specified tool script, stream its output."""
    tools = tool_list(add_class=True)

    # Get script name and optional arguments from the POST request
    object_name = request.json.get('object_name')
    tool_name = request.json.get('tool_name')

    if not object_name or not tool_name:
        logging.warning(f"Request Path: {request.path} - Script name or tool name not provided")
        return {"status": "error", "message": "Script name or tool name not provided."}, 400

    if object_name not in tools.keys():
        logging.error(f"Request Path: {request.path} - The script {object_name} was not found")
        return {"status": "error", "message": f"Script not found, available options are {', '.join(tools.keys())}"}, 404

    if tool_name not in tools[object_name].keys():
        logging.error(f"Request Path: {request.path} - The tool {tool_name} was not found in script {object_name}")
        return {"status": "error", "message": f"Tool not found in script {object_name}"}, 404

    class QueueHandler(logging.Handler):
        def __init__(self, q):
            super().__init__()
            self.q = q

        def emit(self, record):
            msg = self.format(record)
            self.q.put(msg + '\n')

    func = tools[object_name][tool_name].get("run_fun", None)
    if func is None:
        logging.error(f"Not run_fun in {object_name} - {tool_name}")
        return {"status": "error", "message": f"Not run_fun in {tool_name}"}, 404

    def generate_log_output(func):
        """ Run the function and capture its logging output"""
        q = queue.Queue()

        def run_and_capture():
            handler = QueueHandler(q)
            handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            try:
                func()
            finally:
                root_logger.removeHandler(handler)
                q.put(None)  # to stop thread

        thread = threading.Thread(target=run_and_capture)
        thread.start()

        while True:
            msg = q.get()
            if msg is None:
                break
            yield msg

    return Response(generate_log_output(func), content_type='text/plain')

@api_bp.route('/api/save_params', methods=['POST'])
def save_params() -> Tuple[Dict[str, Any], int]:
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
        return {"status": "error", "message": f"Config file for {config_file} not found"}, 404

    if tool_name not in config:
        config[tool_name] = {}

    for param_name, param_value in params.items():
        config[tool_name][param_name] = str(param_value)

    with open(config_file, 'w') as cf:
        config.write(cf)

    return {"status": "success", "message": "Parameters saved successfully"}, 200


@api_bp.route('/api/set_log_level', methods=['POST'])
def set_log_level() -> Tuple[Dict[str, Any], int]:
    data = request.json or {}
    log_level = data.get('log_level', '').upper()

    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level not in valid_levels:
        return {"status": "error", "message": f"Invalid log level. Valid levels are: {', '.join(valid_levels)}"}, 400

    logging.getLogger().setLevel(log_level)
    logging.info(f"Log level changed to {log_level}")
    return {"status": "success", "message": f"Log level set to {log_level}"}, 200

# --------------------- ORDER/EDIT ----------------
@api_bp.route('/api/toggle_source', methods=['POST'])
def enable_disable_source() -> Tuple[Dict[str, Any], int]:
    data = request.json or {}
    source_name = data.get('source_name', None)
    enabled = data.get('enabled', None)
    if source_name is None or enabled is None:
        return {"status": "error", "message": "Parameters source_name and enabled are required"}, 400
    if enabled == 'true':
        manager.toggle_source(source_name, True)
        return {"status": "success", "message": f"Parameter enabled set to {enabled}"}, 200
    if enabled == 'false':
        manager.toggle_source(source_name, False)
        return {"status": "success", "message": f"Parameter enabled set to {enabled}"}, 200
    return {"status": "error", "message": "Parameters have invalid values"}, 400


@api_bp.route('/api/order_sources', methods=['POST'])
def order_sources() -> Tuple[Dict[str, Any], int]:
    data = request.json
    source_order = data.get('source_order', None)
    if not isinstance(source_order, list):
        return {"status": "error", "message": "source_order must be a list"}, 400
    try:
        GlobalConfig().save_ordered_sources(source_order)
        return {"status": "success", "message": "Source order saved"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@api_bp.route('/api/map_settings')
def map_settings():
    settings = GlobalConfig().get_map_settings()
    return jsonify(settings)