import configparser
import logging
from abc import abstractmethod
from typing import Any, Dict, Optional

from sqlalchemy import Column, Table, UniqueConstraint, String, inspect, text, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression

from formator.bssid import format_bssid
from map_app.source_core.Source import MapSource
from map_app.source_core.db import Database
from map_app.source_core.manager import _load_source_objects


#---------------------Table_v0----------------------
# Table_v0 is typical table to make some sources more generic
# check create_table to see table format
class Table_v0(MapSource):

    # ------------CONFIG----------------
    def __init__(self, table_name: str = None, config: Optional[Dict[str, Any]] = None):
        self.SOURCE_NAME: str = table_name
        if table_name is None:
            self.SOURCE_NAME = "tablev0" # tablev0 only like tool source
            return
        #tablev0 table to save to active plugins
        if "tablev0_tables" in Database().metadata.tables:
            self.tablev0_tables_sql = Database().metadata.tables["tablev0_tables"]
        else:
            if not inspect(Database().engine).has_table("tablev0_tables"):
                self.tablev0_tables_sql = Table(
                    "tablev0_tables", Database().metadata,
                    Column("name", String, primary_key=True),
                    extend_existing=True
                )
            else:
                self.tablev0_tables_sql = Table(
                    "tablev0_tables",
                    Database().metadata,
                    autoload_with=Database().engine
                )

            Database().metadata.create_all(Database().engine)


        if table_name is not None:
            with Database().get_db_connection() as conn:
                conn.execute(
                    self.tablev0_tables_sql.insert().prefix_with("OR IGNORE"),
                    {"name": table_name}
                )


        # create table if not exists
        if self.SOURCE_NAME in Database().metadata.tables:
            self.table = Database().metadata.tables[self.SOURCE_NAME]
        else:
            if not inspect(Database().engine).has_table(self.SOURCE_NAME):
                self.table = self.create_table(self.SOURCE_NAME)
                Database().metadata.create_all(Database().engine)
            else:
                self.table = Table(self.SOURCE_NAME, Database().metadata, autoload_with=Database().engine)

        # Dynamically create a mapped class
        if self.SOURCE_NAME not in Database().metadata.tables:
            type(self.SOURCE_NAME, (Database().Base,), {
                '__tablename__': self.SOURCE_NAME,
                '__table__': self.table
            })
        super().__init__(table_name, config)

        default_config = configparser.ConfigParser()
        default_config['table_v0'] = {
            'block_duplicates': 'true',
        }
        self.create_config(self.config_path("table_v0"), default_config)


    def _new_row(self, bssid ) -> bool: # true if it new
        config = configparser.ConfigParser()
        config.read(self.config_path("table_v0"))

        # ignore
        if config['table_v0']['block_duplicates'] == 'false':
            return True

        table_names = Table_v0.get_tablev0_tables()
        if not table_names:
            return True  # No tables to check, so allow insert

        union_queries = [
            f"SELECT 1 FROM {table_name} WHERE bssid = :bssid"
            for table_name in table_names
        ]

        full_query = " UNION ALL ".join(union_queries) + " LIMIT 1"

        with Database().get_db_connection() as conn:
            result = conn.execute(text(full_query), {"bssid": bssid}).first()
            return result is None

    def __remove_duplicates(self):
        #in reload/insert meyhods check if in already in
        pass

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        config = configparser.ConfigParser()
        config.read(self.config_path("table_v0"))
        global_param = [("block_duplicates", str, None, config['table_v0']['block_duplicates'], "Block insert of duplicates betweeb tablec0 tables"), ]
        return {
            "Table_v0": {"params":global_param},
            "remove_duplicates": {"run_fun": self.__remove_duplicates},
            "tablev0_locate": {"run_fun": Table_v0.table_v0_locate}
        }

    @staticmethod
    def create_table(table_name) -> Table:
        return Table(table_name, Database().metadata,
            Column('bssid', String, primary_key=True),
            Column('encryption', String),
            Column('essid', String),
            Column('password', String),
            Column('time', String),
            Column('latitude', String),
            Column('longitude', String),
            Column('last_locate_try', String),
            UniqueConstraint('bssid', 'essid', name=f'{table_name}_ap_sta_ssid_uc'),
            extend_existing=True
        )

    def get_map_data(self,filters: Optional[Dict[str, Any]]=None):
        if  self.SOURCE_NAME is None:
            raise  NotImplementedError
        with Database().get_db_connection() as session:
            table = Table(self.SOURCE_NAME, Database().metadata, autoload_with=Database().engine)

            table_v0_query = expression.select(
                table.c.bssid,
                table.c.encryption,
                table.c.essid,
                table.c.password,
                table.c.latitude,
                table.c.longitude
            ).distinct().where(
                (table.c.latitude.is_not(None)) & (table.c.longitude.is_not(None))
            )

            limit = None
            if filters is not None  and 'limit' in filters:
                limit = int(filters.pop('limit', None))

            regex = False
            if filters is not None and 'regex' in filters:
                regex = filters.pop('regex')

            if filters is not None and 'center_latitude' in filters and 'center_longitude' in filters:
                pass
            else:
                if filters:
                    logging.info("Filters:", filters)
                    for key, value in filters.items():
                        column = getattr(table.c, key, None)
                        if column is not None:
                            if regex and key in ('essid', 'bssid'):
                                table_v0_query = table_v0_query.where(column.op("REGEXP")(value))
                            else:
                                table_v0_query = table_v0_query.where(column == value)
                        else:
                            logging.error(f"Column {key} does not exist in the table")
            if limit is not None:
                table_v0_query = table_v0_query.limit(limit)
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

    @staticmethod
    def get_tablev0_tables():
        return  _load_source_objects(Table_v0)
        #from src.map_app.source_core.db import Database
        #Database().metadata.reflect(bind=Database().engine)
        #table = Database().metadata.tables.get("tablev0_tables")
        #if table is None:
        #    return []
        #with Database().engine.connect() as conn:
        #    result = conn.execute(select(table.c.name))
        #    return [row[0] for row in result.fetchall()]

    @staticmethod
    def table_v0_locate() -> None:
        from src.map_app.sources.wigle import Wigle
        table_names = Table_v0.get_tablev0_tables()
        logging.info(f"Active tablev0_tables: {table_names}")
        for table_v0_name in table_names:
            logging.info(f"{table_v0_name}: Starting data localization")
            localized_networks, total_networks = Wigle().wigle_locate(table_v0_name)
            logging.info(f"{table_v0_name}: Located {localized_networks} out of {total_networks} networks")

    def _save_AP_to_db(self, bssid=None, essid=None, password=None, time=None,
                       bssid_format=False, session= None) -> bool:

        if bssid_format:
            bssid=format_bssid(bssid)

        new_tablev0_entry = {
            'bssid': bssid,
            'essid': essid,
            'password': password,
            'time': time
        }

        try:
            session.execute(self.table.insert().values(new_tablev0_entry))
            logging.info(f"New network: {essid}")
            return True
        except IntegrityError as e:
            if "UNIQUE constraint failed" in str(e.orig):
                return False
            else:
                raise
