import configparser
import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from requests import ReadTimeout
from sqlalchemy import select, Table, update, Connection

from formator.param_validator import valid_wigle_key
from map_app.source_core.MapSource import MapSource
from map_app.source_core.ToolSource import ToolGenerator
from map_app.source_core.db import Database


class Wigle(MapSource):
    __description__ = "Tools to get localization for access point from wigle(https://wigle.net/)"

    def __init__(self):
        super().__init__("wigle")

        default_config = configparser.ConfigParser()
        default_config['wigle_locate'] = {
            'api_keys': '<your_wigle_api_key_here>',
            'locate_older_than_days': 7
        }
        default_config['wigle_view'] = {
            'database_name': 'wigle_wpa3',
            'download_params': '{"encryption": "WPA3", "country": "CZ"}'
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
                session.execute(update(table).where(table.c.bssid == bssid).values(
                    encryption=encryption,
                    latitude=latitude,
                    longitude=longitude,
                    time=time,
                    essid=essid,
                    password=password
                ))
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

    def wigle_download_to_sql(self):
        import os, json, logging, sqlite3, configparser, requests

        config = configparser.ConfigParser()
        config.read(self.config_path())

        db_name = config.get('wigle_view', 'database_name')
        raw_params = config.get('wigle_view', 'download_params')
        params = json.loads(raw_params.replace("'", '"'))

        api_key = self.__get_api_key()
        url = "https://api.wigle.net/api/v2/network/search"
        headers = {"Authorization": f"Basic {api_key}"}

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        db_path = os.path.abspath(os.path.join(base_dir, f"data/raw/wigle/{db_name}.db"))
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS wigle_networks
                       (
                           bssid      TEXT PRIMARY KEY,
                           ssid       TEXT,
                           encryption TEXT,
                           trilat     REAL,
                           trilong    REAL,
                           country    TEXT,
                           city       TEXT,
                           lasttime   TEXT
                       )
                       """)

        total_downloaded = 0
        start = 0
        page_size = 100

        while True:
            paged_params = params.copy()
            paged_params['start'] = start
            paged_params['resultsPerPage'] = page_size

            response = requests.get(url, params=paged_params, headers=headers, timeout=40)
            if response.status_code != 200:
                logging.error(f"Download error: {response.status_code}")
                break

            json_data = response.json()
            results = json_data.get('results', [])
            total_results = json_data.get('totalResults', 0)

            if start >= total_results:
                logging.info("Reached all available results, ending download.")
                break

            if not results:
                logging.info("No results returned, ending download.")
                break

            for entry in results:
                cursor.execute("""
                    INSERT OR REPLACE INTO wigle_networks
                    (bssid, ssid, encryption, trilat, trilong, country, city, lasttime)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.get('netid'),
                    entry.get('ssid'),
                    entry.get('encryption'),
                    entry.get('trilat'),
                    entry.get('trilong'),
                    entry.get('country'),
                    entry.get('city'),
                    entry.get('lasttime')
                ))
            conn.commit()

            total_downloaded += len(results)
            logging.info(f"Downloaded {len(results)} APs in this batch. Total downloaded: {total_downloaded}")

            start += len(results)

            if len(results) < page_size:
                logging.info("Last batch received, ending download.")
                break

        conn.close()
        logging.info(f"Download complete. Total APs downloaded: {total_downloaded}")
        return total_downloaded

    def get_tools(self):
        gen = ToolGenerator(self)

        gen.addParam(tool_name="wigle_locate",
                     param_name="api_keys",
                     #validation_function=valid_wigle_key,
                     description="Key for Wigle")
        gen.addParam(tool_name="wigle_locate",
                     param_name="locate_older_than_days",
                     input_type=int,
                     validation_function=int,
                     description="Check localization older than")
        gen.add_run_fun(tool_name="wigle_locate", run_fun=self.wigle_locate)

        print(self.config_path())
        gen.addParam(tool_name="wigle_view",
                     param_name="database_name",
                     description="Name of sql database in /data/raw/wigle/")
        gen.addParam(tool_name="wigle_view",
                     param_name="download_params",
                     description="Filter for download")
        gen.add_run_fun(tool_name="wigle_view", run_fun=self.wigle_download_to_sql)
        return gen.get_list()

    def get_map_data(self, filters: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        config = configparser.ConfigParser()
        config.read(self.config_path())
        db_name = config.get('wigle_view', 'database_name')
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        db_path = os.path.abspath(os.path.join(base_dir, f"data/raw/wigle/{db_name}.db"))

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = "SELECT bssid, ssid, encryption, trilat, trilong FROM wigle_networks"
        params = []
        if filters:
            clauses = []
            for key, value in filters.items():
                clauses.append(f"{key} = ?")
                params.append(value)
            if clauses:
                query += " WHERE " + " AND ".join(clauses)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        # Map columns to required output keys
        return [
            {
                "bssid": row[0],
                "encryption": row[2],
                "essid": row[1],
                "password": None,
                "latitude": row[3],
                "longitude": row[4]
            }
            for row in rows
        ]