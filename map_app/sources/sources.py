import os
import inspect

from sqlalchemy import Table, MetaData
from sqlalchemy.sql import expression

from map_app.tools.db import get_db_connection, engine

BASE_FILE = os.path.dirname(os.path.abspath(__file__))
sources_config_file = os.path.join(BASE_FILE,'..','sources','config')
os.makedirs(sources_config_file, exist_ok=True)

def config_path():
    frame = inspect.stack()[1]
    calling_script = frame[1]
    script_name = os.path.splitext(os.path.basename(calling_script))[0]
    return f'{sources_config_file}/{script_name}.ini'

#TODO
#---------------------Table_v0----------------------
#Table_v0: Typycal table and help functions for sources


def get_map_data(TABLE_NAME,filters=None):
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
                    if hasattr(table.c, key):
                        table_v0_query = table_v0_query.where(getattr(table.c, key) == value)
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