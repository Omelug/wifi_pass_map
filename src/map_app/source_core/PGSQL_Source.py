import configparser
from typing import Dict, Any
from src.map_app.source_core.Source import MapSource

class PGSQL_MapSource(MapSource):
    DEFAULT_SOURCE_NAME = "pgsql_mapsource"
    def __init__(self, database_name = None, config = None):
        self.SOURCE_NAME = database_name
        if database_name is None:
            self.SOURCE_NAME = PGSQL_MapSource.DEFAULT_SOURCE_NAME
            return
        super().__init__(database_name, config)

        default_config = configparser.ConfigParser()
        default_config[PGSQL_MapSource.DEFAULT_SOURCE_NAME] = {
            'db_user': 'postgres',
            'db_pass': '',
            'db_ip': 'localhost',
            'db_port': '5432',
            'db_name': 'wifi_pass_map',
        }
        self.create_config(self.config_path(PGSQL_MapSource.DEFAULT_SOURCE_NAME), default_config)

    def get_tools(self) -> Dict[str, Dict[str, Any]]|None:
        config = configparser.ConfigParser()
        if not config.read(self.config_path(PGSQL_MapSource.DEFAULT_SOURCE_NAME)):
            return None
        global_param = [
            ("db_user", str, None, config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_user'], "postgres SQL user"),
            ("db_pass", str, None, config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_pass'], "postgres SQL password"),
            ("db_ip", str, None, config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_ip'], "postgres SQL ip"),
            ("db_port", str, None, config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_port'], "postgres SQL port"),
            ("db_name", str, None, config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_name'], "postgres SQL database name"),
        ]
        return {
            self.DEFAULT_SOURCE_NAME : {"params":global_param}
        }

    def connection_link(self, dbname=None, eq_str=False):
        config = configparser.ConfigParser()
        config.read(self.config_path(PGSQL_MapSource.DEFAULT_SOURCE_NAME))

        user = config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_user']
        password = config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_pass']
        host = config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_ip']
        port = config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_port']
        if dbname is None:
            dbname = config[PGSQL_MapSource.DEFAULT_SOURCE_NAME]['db_name']
        if eq_str:
            return f"PG:\"host={host} dbname={dbname} user={user} password={password} port={port}\""
        return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"