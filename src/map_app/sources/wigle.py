import configparser
import logging
import sqlite3
from typing import Dict, Any
import requests
import random
from requests import ReadTimeout
from sqlalchemy import select, Table, update, Connection

from map_app.source_core.ToolSource import ToolSource
from map_app.source_core.db import Database
from datetime import datetime,timedelta

class Wigle(ToolSource):
    __description__ = "Tools to get localization for access point from wigle(https://wigle.net/)"

    def __init__(self):
        super().__init__("wigle")

        default_config = configparser.ConfigParser()
        default_config['wigle_locate'] = {
            'api_keys': '<your_wigle_api_key_here>',
            'locate_older_than_days': 7
        }

        self.create_config(config=default_config)

    def __get_api_key(self) -> str:
        config = configparser.ConfigParser()
        config.read(self.config_path())
        return config['wigle_locate']['api_keys'].split(',')[0]


    # table_name - in this table shoud be bssid, password,
    def _save_wigle_location(
            self,
            wigle_data: Dict[str, Any],
            session: Connection,
            table: Table,
            bssid: str,
            password: str
    ) -> bool:
        logging.info(wigle_data)
        results = wigle_data.get('results', [])
        if results:
            result = results[0]
            essid = result.get('ssid')
            encryption = result.get('encryption')
            latitude = result.get('trilat')
            longitude = result.get('trilong')
            time = result.get('lasttime')
            logging.info(f"✅📌 Found geolocation for {essid}({bssid}) - {latitude}, {longitude}")
            try:
                query = update(table).where(table.c.bssid == bssid).values(
                    encryption=encryption,
                    latitude=latitude,
                    longitude=longitude,
                    time=time,
                    essid=essid,
                    password=password
                )
                logging.info(query)
                session.execute(query)
                return True
            except sqlite3.Error as e:
                logging.info(f"{self.SOURCE_NAME} Got error {e} when inserting entry for bssid: {bssid}")
                return False

        logging.info(f"❌ No geolocation for {bssid} found...")
        query = update(table).where(table.c.bssid == bssid).values(
            last_locate_try=datetime.now()
        )
        logging.info(query)
        session.execute(query)
        return False

    def wigle_locate(self,table_name:str) -> (int, int):
        localized_networks = total_networks = 0

        table = Table(table_name, Database().metadata, autoload_with=Database().engine)

        with Database().get_db_connection() as session:
            try:

                config = configparser.ConfigParser()
                config.read(self.config_path())

                # Get days from config and calculate cutoff datetime
                days = int(config['wigle_locate']['locate_older_than_days'])
                cutoff = datetime.now() - timedelta(days=days)

                not_localized_q = select(table.c.bssid, table.c.password).distinct().where(
                    (
                            (table.c.latitude.is_(None)) | (table.c.longitude.is_(None))
                    ) &
                    (
                            (table.c.last_locate_try.is_(None)) |
                            (table.c.last_locate_try < cutoff)
                    )
                ).order_by(table.c.last_locate_try.is_(None), table.c.last_locate_try)

                wpasec_data = session.execute(not_localized_q).fetchall()

                #shuffle data to increase chance for hits for the next day when running into the API Limit
                api_key = Wigle().__get_api_key()
                logging.info(f"{self.SOURCE_NAME} API key loaded, try check {len(wpasec_data)} networks")

                for row in wpasec_data:
                    bssid, password = row
                    bssid = bssid.lower()

                    total_networks += 1

                    response = requests.get(
                        f"https://api.wigle.net/api/v2/network/search?netid={bssid}",
                        headers={"Authorization": f"Basic {api_key}"},
                        timeout=40
                    )

                    if response.status_code == 401:
                        logging.info(f"The {self.SOURCE_NAME} API {api_key} Key is not authorized. Validate it in the Settings")
                        break
                    elif response.status_code == 429:
                        logging.info("❌ Received status code 429: API Limit reached.")
                        break
                    elif response.status_code == 200:
                        try:
                            wigle_data = response.json()
                            localized_networks += Wigle()._save_wigle_location(wigle_data, session, table, bssid, password)
                            session.commit() # update after each request, because main limit is wigle API limit
                        except ValueError as e:
                            logging.info(f"Error parsing JSON response: {e}")
                            break
                    else:
                        logging.info(f"Error retrieving data for {bssid}. Status code: {response.status_code}")
                        break
            except ReadTimeout as  e:
                logging.info(f"Timeout error: {e}")
        return localized_networks, total_networks

    def get_tools(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        wigle_param = [("api_keys", str, None, config['wigle_locate']['api_keys'], "Key for Wigle"),
                       ("locate_older_than_days", int, None, config['wigle_locate']['locate_older_than_days'], "Check localization older than")]
        return {"wigle":{"params":wigle_param}}




