import importlib.util
import inspect
import logging
import os
import traceback
from typing import Dict, List, Any, Tuple, Optional

from attr.validators import disabled

from map_app.source_core.GlobalConfig import GlobalConfig
from map_app.source_core.Source import ToolSource, MapSource

BASE_FILE = os.path.dirname(os.path.abspath(__file__))

def tool_name_list(disabled:bool = True):
    """Get all enabled tools sources"""
    script_paths = []
    # add special prototypes from /source_core/ (for general tools)
    tablev_v_path = os.path.join(BASE_FILE, '..', 'source_core', 'Table_v0.py')
    script_paths.append(os.path.abspath(tablev_v_path))

    global_config_path = os.path.join(BASE_FILE, '..', 'source_core', 'GlobalConfig.py')
    script_paths.append(os.path.abspath(global_config_path))

    SOURCE_DIR = os.path.join(BASE_FILE,'..', "sources")
    script_paths.extend([os.path.join(root, f) for root, _, files in os.walk(SOURCE_DIR) for f in files if f.endswith('.py') and (disabled or not f.endswith('.disable.py'))])
    return script_paths


def order_sources_by_config(source_names: list) -> list:
    order = GlobalConfig().get_ordered_sources()
    ordered = []
    used = set()
    for name in order:
        if name in source_names:
            ordered.append(name)
            used.add(name)
    for name in sorted(source_names):
        if name not in used:
            ordered.append(name)
    return ordered

def get_sources_with_status():
    sources_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sources"))

    sources = {}
    for fname in os.listdir(sources_dir):
        if fname.endswith('.py') and not fname.endswith('.disable.py'):
            name = fname[:-3]
            sources[name] = True
        elif fname.endswith('.disable.py'):
            name = fname[:-11]
            sources[name] = False
    #print("sources", sources)
    valid_names = {type(obj).__name__.lower() for obj in _load_source_objects(ToolSource, True)}
    #print("valid_names", valid_names)
    sources = {name: enabled for name, enabled in sources.items() if name in valid_names}
    #print("sources", sources)

    ordered_names = order_sources_by_config(list(sources.keys()))
    return [{'name': name, 'enabled': sources[name]} for name in ordered_names]

def _load_source_objects(Source_class, disabled:bool = False) -> List[Any]:
    """Dynamically load source classes and create instances if they are children of Source_class."""
    script_paths = tool_name_list(disabled)
    source_objects = []

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

    # Order by config
    name_to_obj = {type(obj).__name__.lower(): obj for obj in source_objects}
    ordered_names = order_sources_by_config(list(name_to_obj.keys()))
    return [name_to_obj[name] for name in ordered_names if name in name_to_obj]

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

def toggle_source(source_name: str, enable: bool):

    BASE_FILE = os.path.dirname(os.path.abspath(__file__))
    SOURCES_DIR = os.path.join(BASE_FILE, '..', 'sources')
    src_file = os.path.join(SOURCES_DIR, f"{source_name}.py")
    disabled_file = os.path.join(SOURCES_DIR, f"{source_name}.disable.py")

    if enable:
        if os.path.exists(disabled_file):
            os.rename(disabled_file, src_file)
    else:
        if os.path.exists(src_file):
            os.rename(src_file, disabled_file)
