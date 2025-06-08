import importlib.util
import inspect
import logging
import os
import traceback
from typing import Dict, List, Any, Tuple, Optional
from map_app.source_core.Source import ToolSource, MapSource

BASE_FILE = os.path.dirname(os.path.abspath(__file__))

def _load_source_objects(Source_class) -> List[Any]:
    """Dynamically load source classes and create instances if they are children of DBSource."""
    source_objects = []

    script_paths = []
    # add special prototypes from /source_core/ (for general tools)
    tablev_v_path = os.path.abspath(os.path.join(BASE_FILE, '..', 'source_core', 'Table_v0.py'))
    script_paths.append(tablev_v_path)

    SOURCE_DIR = os.path.join(BASE_FILE,'..', "sources")
    script_paths.extend([os.path.join(root, f) for root, _, files in os.walk(SOURCE_DIR) for f in files if f.endswith('.py')])

    for script_path in script_paths:
        try:
            spec = importlib.util.spec_from_file_location("source_module", script_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Source_class) and obj.__module__ == module.__name__:
                        source_objects.append(obj())
        except Exception as e:
            logging.error(f"Error loading module from {script_path}: {e}")

            logging.error(traceback.format_exc())
    return source_objects

def tool_list(add_class=False) -> dict:
    """Get tool lists from sources using get_tools(), adding object_name to each tool."""
    tools = {}
    source_objects = _load_source_objects(ToolSource)
    for source_obj in source_objects:
        if hasattr(source_obj, 'get_tools'):
            object_name = type(source_obj).__name__.lower()
            tools[object_name] = source_obj.get_tools()
            if add_class:
                tools[object_name]["class"] = type(source_obj)
        else:
            logging.warning(f"{type(source_obj).__name__} does not have a get_tools() function")
    return tools


def get_AP_data(filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Get data from source sources using get_map_data()."""

    pwned_data: List[Dict[str, Any]] = []
    script_statuses: List[Dict[str, Any]] = []

    for source_obj in _load_source_objects(MapSource):
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
            except NotImplementedError: # ignore 'abstract' plugins
                pass
            except Exception as e:
                script_statuses.append({'name': object_name, 'status': 'failed'})
                logging.error(f"Error processing data from {object_name}: {e}")
                logging.error(traceback.format_exc())
        else:
            logging.debug(f"{object_name} does not have a get_map_data() function")
            script_statuses.append({'name': object_name, 'status': 'missing_function'})

    return pwned_data, script_statuses
