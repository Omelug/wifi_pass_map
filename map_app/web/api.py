import importlib.util

from flask import jsonify, request, Response, stream_with_context, Blueprint, session, send_file
import sqlite3, os, subprocess, re, logging
from werkzeug.utils import secure_filename

from formator.files import sanitize_filename
import map_app.tools.tool_management as tool_management

api_bp = Blueprint('api', __name__)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

POT_UPLOAD_FOLDER = 'app/data/potfile'
ALLOWED_EXTENSIONS = {'pot', '22000', 'potfile'}

tools = tool_management.tool_list()

@api_bp.route('/api/tools', methods=['POST'])
def run_script():
    # Get script name and optional arguments from the POST request
    script_name = request.json.get('script_name')

    if not script_name:
        log.warning(f"Request Path: {request.path} - No script was provided")
        return {"status": "error", "message": "Script name not provided."}, 400

    if script_name not in tools.keys():
        log.error(f"Request Path: {request.path} - The script {script_name} was not found")
        return {"status": "error", "message": f"Script not found, available options are {', '.join(tools.keys())}"}, 404

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

    func = tools[script_name]
    return Response(stream_with_context(generate_output(func)), content_type='text/plain')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api_bp.route('/api/pot_upload', methods=['POST'])
def upload_pot():
    if 'file' not in request.files:
        return {"status": "error", "message": "No file part"}, 400
    file = request.files['file']
    if file.filename == '':
        return {"status": "error", "message": "No selected file"}, 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(POT_UPLOAD_FOLDER, filename))
        return {"status": "success", "message": "File uploaded successfully"}, 200
    else:
        return {"status": "error", "message": "File type not allowed"}, 400


@api_bp.route('/api/wardrive', methods=['GET'])
def get_street_overlay():
    log.info(f"Current working directory: {os.getcwd()}")

    geojson_file = "app/data/wardrive/wardrive_overlay.json"
    log.debug(f"GeoJSON file path: {geojson_file}")

    # Check if the file exists before attempting to serve it
    if os.path.exists(geojson_file):
        return send_file(geojson_file, as_attachment=False, download_name="wardrive_overlay")
    else:
        return {"error": "GeoJSON wardrive overlay not found"}, 404

@api_bp.route('/api/wifi_pass_map')
def pwnapi():
    log.debug(f"Request Path: {request.path} was called")

    SOURCE_DIR = './map_app/sources'

    pwned_data,script_statuses = [],[]

    # Get list of scripts which gives data from various sources
    source_scripts = [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.py')]
    for script_path in source_scripts:
        print(f"Loading data from {script_path}")
        script_name = os.path.basename(script_path)
        try:
            # Dynamically import the source script
            spec = importlib.util.spec_from_file_location("source_module", script_path)
            source_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(source_module)

            # Call the get_map_data()
            if hasattr(source_module, 'get_map_data'):
                data = source_module.get_map_data()
                if data:
                    script_statuses.append({'name': script_name, 'status': 'success'})
                    pwned_data.extend(data)
                else:
                    script_statuses.append({'name': script_name, 'status': 'empty'})

            else:
                log.warning(f"{script_path} does not have a get_map_data() function")
        except Exception as e:
            script_statuses.append({'name': script_name, 'status': 'failed'})
            log.error(f"Error loading data from {script_path} A: {e}")
        print(f"{script_path} data loaded A")

    return jsonify({
        'data': pwned_data,
        'script_statuses': script_statuses,
        'AP_len': len(pwned_data)
    })

@api_bp.route('/api/upload', methods=['POST'])
def upload_file():

    # Check for file in request
    if 'file' not in request.files:
        log.warning("Request Path: {request.path} - No file in request ")
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    # Check if file name is empty
    if file.filename == '':
        log.warning("Request Path: {request.path} - No filename in request ")
        return jsonify({'error': 'No file selected for uploading'}), 400

    filename = sanitize_filename(file.filename)

    # Directory where files are stored
    data_dir = "map_app/data/handshakes/"
    file_path = os.path.join(data_dir, filename)

    # Check if file already exists
    if os.path.exists(file_path):
        log.info("Request Path: {request.path} - File already submitted ")
        return jsonify({'message': 'Already submitted'}), 200

    file.save(file_path)
    return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
