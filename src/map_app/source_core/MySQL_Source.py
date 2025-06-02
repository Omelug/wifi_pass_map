import configparser
import logging
import os
import warnings

from sqlalchemy import inspect, create_engine, exc

from src.map_app.source_core.MapSource import MapSource
from src.map_app.sources import config_path


#---------------------MySQL_Source----------------------
class MySQL_MapSource(MapSource):

    def __init__(self, database_name, default_config):
        super().__init__(database_name)

        #default config values
        conf_path = config_path(self.SOURCE_NAME)
        if not os.path.exists(conf_path):
            with open(conf_path, 'w') as config_file:
                default_config.write(config_file)
            logging.info(f"{self.SOURCE_NAME} configuration created {conf_path}")

    def _get_db_connection(self):
        config = configparser.ConfigParser()
        config.read(config_path(self.SOURCE_NAME))

        db_user = config['MAIN']['db_user']
        db_pass = config['MAIN']['db_pass']
        db_ip = config['MAIN']['db_ip']
        db_name = config['MAIN']['db_name']

        engine = create_engine(
            f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_ip}/{db_name}',
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