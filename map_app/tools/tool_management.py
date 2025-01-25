import logging
import os
import importlib.util

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def tool_list():
    SOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sources")
    source_scripts = [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.py')]

    tools = {}
    for script_path in source_scripts:
        try:
            # Dynamically import the source script
            spec = importlib.util.spec_from_file_location("source_module", script_path)
            source_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(source_module)

            if hasattr(source_module, 'get_tools'):
                module_tools = source_module.get_tools()
                #print(f"{script_path} has tools: {module_tools}\n\n\n")
                tools.update(module_tools)
            else:
                log.warning(f"{script_path} does not have a get_tools() function")
        except Exception as e:
            log.error(f"Error loading data from {script_path} B: {e}")
        print(f"{script_path} data loaded B")
    return tools


def get_AP_data(filters=None, center=None, sqare_limit=None):
    pwned_data, script_statuses = [], []
    SOURCE_DIR = './map_app/sources'

    # Get list of scripts which gives data from various sources
    source_scripts = [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.py')]
    for script_path in source_scripts:
        print(f"Loading data from {script_path}")
        script_name = os.path.basename(script_path)
        try:
            #Dynamically import the source scripts
            spec = importlib.util.spec_from_file_location("source_module", script_path)
            source_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(source_module)

            # Call the get_map_data()
            if hasattr(source_module, 'get_map_data'):
                data = source_module.get_map_data(filters.copy() if filters else None) # Tell sources to use filters
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
    return pwned_data, script_statuses
