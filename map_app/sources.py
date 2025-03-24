import inspect
import logging
import os
import importlib.util
import traceback
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import Table, MetaData
from sqlalchemy.sql import expression
from map_app.tools.db import get_db_connection, engine

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

BASE_FILE = os.path.dirname(os.path.abspath(__file__))
sources_config_file = os.path.join(BASE_FILE,'sources','config')
os.makedirs(sources_config_file, exist_ok=True)


def source_scripts() -> List[str]:
    """Get .py source files in /sources"""
    SOURCE_DIR = os.path.join(BASE_FILE, "sources")
    return [os.path.join(SOURCE_DIR, f) for f in os.listdir(SOURCE_DIR) if f.endswith('.py')]

def load_source_module(script_path: str) -> Optional[Any]:
    """Dynamically load script module"""
    try:
        spec = importlib.util.spec_from_file_location("source_module", script_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    except Exception as e:
        log.error(f"Error loading module from {script_path}: {e}")
        log.error(traceback.format_exc())
    return None

def tool_list() -> Dict[str, Any]:
    """Get tool lists from sources using get_tools()"""
    tools = {}
    for script_path in source_scripts():
        module = load_source_module(script_path)
        if module and hasattr(module, 'get_tools'):
            script_name = os.path.splitext(os.path.basename(script_path))[0]
            tools[script_name] = module.get_tools()
        else:
            log.warning(f"{script_path} does not have a get_tools() function")
    return tools


def get_AP_data(filters=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Get data from source sources using get_map_data()."""

    pwned_data: List[Dict[str, Any]] = []
    script_statuses: List[Dict[str, Any]] = []

    for script_path in source_scripts():
        script_name = os.path.basename(script_path)
        module = load_source_module(script_path)

        if module and hasattr(module, 'get_map_data'):
            try:
                data = module.get_map_data(filters.copy() if filters else None)
                if data:
                    for ap_point in data:
                        ap_point['source'] = script_name
                    script_statuses.append({'name': script_name, 'status': 'success', 'len': len(data)})
                    pwned_data.extend(data)
                else:
                    script_statuses.append({'name': script_name, 'status': 'empty'})
            except Exception as e:
                script_statuses.append({'name': script_name, 'status': 'failed'})
                log.error(f"Error processing data from {script_path}: {e}")
                log.error(traceback.format_exc())
        else:
            log.debug(f"{script_path} does not have a get_map_data() function")
            script_statuses.append({'name': script_name, 'status': 'missing_function'})

    return pwned_data, script_statuses


def config_path():
    frame = inspect.stack()[1]
    calling_script = frame[1]
    script_name = os.path.splitext(os.path.basename(calling_script))[0]
    return f'{sources_config_file}/{script_name}.ini'


#---------------------Table_v0----------------------
#Table_v0: Typycal table and help functions for sources

def Table_v0_get_map_data(TABLE_NAME,filters=None):
    with get_db_connection() as session:
        metadata = MetaData()
        table = Table(TABLE_NAME, metadata, autoload_with=engine)

        table_v0_query = expression.select(
            table.c.bssid,
            table.c.encryption,
            table.c.essid,
            table.c.password,
            table.c.latitude,
            table.c.longitude
        ).distinct().where(
            (table.c.latitude.is_not(None)) | (table.c.longitude.is_not(None))
        )

        if filters is not None and 'center_latitude' in filters and 'center_longitude' in filters:
            pass
        else:
            if filters:
                for key, value in filters.items():
                    column = hasattr(table.c, key)
                    if column:
                        table_v0_query = table_v0_query.where(column == value)
                    else:
                        print(f"Column {key} does not exist in the table")
        table_v0_data = session.execute(table_v0_query).fetchall()

        return [
            {
                "bssid": row.bssid,
                "encryption": row.encryption,
                "essid": row.essid,
                "password": row.password,
                "latitude": row.latitude,
                "longitude": row.longitude
            }
            for row in table_v0_data
        ]