import logging
import os
import importlib.util
import traceback

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# get all .py files in sources exclude sources.py
def source_scripts():
    SOURCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sources")
    return [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR)
                      if f.endswith('.py') and not f.endswith('sources.py')]
def tool_list():

    tools = {}
    for script_path in source_scripts():
        try:
            # Dynamically import the source script
            spec = importlib.util.spec_from_file_location("source_module", script_path)
            source_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(source_module)

            if hasattr(source_module, 'get_tools'):
                module_tools = source_module.get_tools()
                script_name = os.path.splitext(os.path.basename(script_path))[0]
                tools[script_name] = module_tools

            else:
                log.warning(f"{script_path} does not have a get_tools() function")
        except Exception as e:
            log.error(f"Error loading data from {script_path} B: {e}")
        print(f"{script_path} data loaded B")
    return tools


def get_AP_data(filters=None):
    pwned_data, script_statuses = [], []

    for script_path in source_scripts():
        #print(f"Loading data from {script_path}")
        script_name = os.path.basename(script_path)
        try:
            #Dynamically import the source scripts
            spec = importlib.util.spec_from_file_location("source_module", script_path)
            source_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(source_module)

            # Call the get_map_data() on sources
            if hasattr(source_module, 'get_map_data'):
                data = source_module.get_map_data(filters.copy() if filters else None) # Tell sources to use filters
                if data:
                    for AP_point in data:
                        AP_point['source'] = script_name
                    script_statuses.append({'name': script_name, 'status': 'success', 'len': len(data)})
                    pwned_data.extend(data)
                else:
                    script_statuses.append({'name': script_name, 'status': 'empty'})

            else:
                log.debug(f"{script_path} does not have a get_map_data() function")
        except Exception as e:
            script_statuses.append({'name': script_name, 'status': 'failed'})
            log.error(f"Error loading data from {script_path} A: {e}")
            log.error(traceback.format_exc())
        #print(f"{script_path} data loaded A")
    return pwned_data, script_statuses
