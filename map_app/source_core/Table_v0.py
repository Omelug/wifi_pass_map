import os
from abc import abstractmethod
from sqlalchemy import Column, Table, UniqueConstraint, String, MetaData, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression

from formator.bssid import format_bssid
from map_app.source_core.Source import Source
from map_app.source_core.db import Base, get_db_connection, engine, metadata, Session
from map_app.sources import config_path
from map_app.tools.wigle_api import wigle_locate


#---------------------Table_v0----------------------
# Table_v0 is typical table to make some sources more generic
class Table_v0(Source):

    @property
    @abstractmethod
    def TABLE_NAME(self):
        """Shoud be case insensite (SQL)"""
        pass

    # ------------CONFIG----------------
    def __init__(self, table_name, config):
        super().__init__(table_name)

        # create table if not exists
        if self.TABLE_NAME in metadata.tables:
            self.table = metadata.tables[self.TABLE_NAME]
        else:
            if not inspect(engine).has_table(self.TABLE_NAME):
                self.table = self.create_table(self.TABLE_NAME)
                metadata.create_all(engine)
            else:
                self.table = Table(self.TABLE_NAME, metadata, autoload_with=engine)

        # Dynamically create a mapped class
        if self.TABLE_NAME not in Base.metadata.tables:
            type(self.TABLE_NAME, (Base,), {
                '__tablename__': self.TABLE_NAME,
                '__table__': self.table
            })

        #default config values
        conf_path = config_path(self.TABLE_NAME)
        if not os.path.exists(conf_path):
            with open(conf_path, 'w') as config_file:
                config.write(config_file)
            print(f"{self.TABLE_NAME} configuration created {conf_path}")

    @staticmethod
    def create_table(table_name):
        """
        Create a table for storing wifi data (same format for all sources)
        """
        return Table(table_name, Base.metadata,
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

    # Typycal table and help functions for sources
    def get_map_data(self,filters=None):
        with get_db_connection() as session:
            metadata = MetaData()
            table = Table(self.TABLE_NAME, metadata, autoload_with=engine)

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

    def table_v0_locate(self):
        print(f"{self.TABLE_NAME}: Starting data localization")
        localized_networks, total_networks = wigle_locate(self.TABLE_NAME)
        print(f"{self.TABLE_NAME}: Located {localized_networks} out of {total_networks} networks")

    def _save_AP_to_db(self, bssid=None, essid=None, password=None, time=None,
                       bssid_format=False) -> bool:

        if bssid_format:
            bssid=format_bssid(bssid)

        new_tablev0_entry = {
            'bssid': bssid,
            'essid': essid,
            'password': password,
            'time': time
        }

        with Session() as session:
            try:
                session.execute(self.table.insert().values(new_tablev0_entry))
                session.commit()
                print(f"New network: {essid}")
                return True
            except IntegrityError:
                session.rollback()
                return False
