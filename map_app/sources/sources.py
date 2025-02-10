import inspect
import os

BASE_FILE = os.path.dirname(os.path.abspath(__file__))
sources_config_file = os.path.join(BASE_FILE,'..','sources','config')
os.makedirs(sources_config_file, exist_ok=True)

def config_path():
    frame = inspect.stack()[1]
    calling_script = frame[1]
    script_name = os.path.splitext(os.path.basename(calling_script))[0]
    return f'{sources_config_file}/{script_name}.ini'