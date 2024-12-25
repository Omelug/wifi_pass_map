import logging
import os
import importlib.util

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def tool_list():
    SOURCE_DIR = './map_app/sources'
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
