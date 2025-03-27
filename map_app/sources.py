import importlib.util
import inspect
import logging
import os
import traceback
from typing import Dict, List, Any, Optional, Tuple
from map_app.source_core.DBSource import DBSource

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

BASE_FILE = os.path.dirname(os.path.abspath(__file__))
sources_config_file = os.path.join(BASE_FILE,'sources','config')
os.makedirs(sources_config_file, exist_ok=True)


#def source_scripts() -> List[str]:
#    """Get .py source files in /sources"""
#    SOURCE_DIR = os.path.join(BASE_FILE, "sources")
#    return [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.py')]

def load_source_objects() -> List[Any]:
    """Dynamically load source classes and create instances if they are children of DBSource."""
    source_objects = []
    SOURCE_DIR = os.path.join(BASE_FILE, "sources")
    for script_path in [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.py')]:
        try:
            spec = importlib.util.spec_from_file_location("source_module", script_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, DBSource) and obj.__module__ == module.__name__:
                        source_objects.append(obj())
        except Exception as e:
            log.error(f"Error loading module from {script_path}: {e}")
            log.error(traceback.format_exc())
    return source_objects

def tool_list(add_class=False) -> Dict[str, Any]:
    """Get tool lists from sources using get_tools()"""
    tools = {}
    source_objects = load_source_objects()
    for source_obj in source_objects:
        if hasattr(source_obj, 'get_tools'):
            object_name = type(source_obj).__name__
            tools[object_name] = source_obj.get_tools()
            if add_class:
                tools[object_name]["class"] = type(source_obj)
        else:
            log.warning(f"{type(source_obj).__name__} does not have a get_tools() function")
    return tools


def get_AP_data(filters=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Get data from source sources using get_map_data()."""

    pwned_data: List[Dict[str, Any]] = []
    script_statuses: List[Dict[str, Any]] = []

    for source_obj in load_source_objects():
        object_name = type(source_obj).__name__

        if hasattr(source_obj, 'get_map_data'):
            try:
                data = source_obj.get_map_data(filters.copy() if filters else None)
                if data:
                    for ap_point in data:
                        ap_point['source'] = object_name
                    script_statuses.append({'name': object_name, 'status': 'success', 'len': len(data)})
                    pwned_data.extend(data)
                else:
                    script_statuses.append({'name': object_name, 'status': 'empty'})
            except Exception as e:
                script_statuses.append({'name': object_name, 'status': 'failed'})
                log.error(f"Error processing data from {object_name}: {e}")
                log.error(traceback.format_exc())
        else:
            log.debug(f"{object_name} does not have a get_map_data() function")
            script_statuses.append({'name': object_name, 'status': 'missing_function'})

    return pwned_data, script_statuses


def config_path(object_name=None)->str:
    if object_name is None:
        frame = inspect.stack()[1]
        calling_script = frame[1]
        object_name = os.path.splitext(os.path.basename(calling_script))[0]
    return f'{sources_config_file}/{object_name}.ini'