import configparser
import logging
import warnings
from typing import Dict, Any, Optional
from sqlalchemy import inspect, create_engine, exc
from src.map_app.source_core.Source import MapSource

#---------------------MySQL_Source----------------------
class MySQL_MapSource(MapSource):
    def get_map_data(self, filters: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        #TODO
        pass

    DEFAULT_SOURCE_NAME = "mysql_mapsource"
    def __init__(self, database_name = None, config = None):
        self.SOURCE_NAME = database_name
        if database_name is None:
            self.SOURCE_NAME = MySQL_MapSource.DEFAULT_SOURCE_NAME
            return
        super().__init__(database_name, config)

        default_config = configparser.ConfigParser()
        default_config[MySQL_MapSource.DEFAULT_SOURCE_NAME] = {
            'db_user': 'root',
            'db_pass': '',
            'db_ip': 'localhost',
            'db_port': '3306',
            'db_name': 'wifi_pass_map',
        }
        self.create_config(self.config_path(MySQL_MapSource.DEFAULT_SOURCE_NAME), default_config)

    def _get_db_connection(self):
        config = configparser.ConfigParser()
        config.read(self.config_path(self.SOURCE_NAME))

        db_user = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_user']
        db_pass = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_pass']
        db_ip = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_ip']
        db_port = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_port']
        db_name = config[ MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_name']

        engine = create_engine(
            f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_ip}:{db_port}/{db_name}',
            connect_args={'charset': 'utf8', 'collation': 'utf8mb4_general_ci'}
        )

        return engine.connect()


    def check_db_connection_and_tables(self, tables_and_columns):
        try:
            with self._get_db_connection() as connection:
                inspector = inspect(connection)
                for table_name, columns in tables_and_columns.items():
                    if not inspector.has_table(table_name):
                        logging.error(f"Error: Required table '{table_name}' does not exist in the database {self.SOURCE_NAME}")
                    else:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore", category=exc.SAWarning)
                            table_columns = [col['name'] for col in inspector.get_columns(table_name)]
                        for column in columns:
                            if column not in table_columns:
                                logging.error(f"Error: Required column '{column}' does not exist in table '{table_name}'")
        except exc.SQLAlchemyError as e:
            logging.error(f"Error: Cannot connect to the database {self.SOURCE_NAME}. Exception: {e}")

    def get_tools(self) -> Dict[str, Dict[str, Any]]| None:
        config = configparser.ConfigParser()
        if not config.read(self.config_path(MySQL_MapSource.DEFAULT_SOURCE_NAME)):
            return None
        global_param = [
            ("db_user", str, None, config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_user'], "mysql user"),
            ("db_pass", str, None, config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_pass'], "mysql password"),
            ("db_ip", str, None, config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_ip'], "mysql ip"),
            ("db_port", str, None, config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_port'], "mysql port"),
            ("db_name", str, None, config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_name'], "mysql database name"),
        ]
        return {
            self.DEFAULT_SOURCE_NAME : {"params":global_param}
        }

    def connection_link(self, dbname=None):
        config = configparser.ConfigParser()
        config.read(self.config_path(MySQL_MapSource.DEFAULT_SOURCE_NAME))

        user = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_user']
        password = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_pass']
        host = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_ip']
        port = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_port']
        if dbname is None:
            dbname = config[MySQL_MapSource.DEFAULT_SOURCE_NAME]['db_name']
        return f"mysql://{user}:{password}@{host}:{port}/{dbname}"