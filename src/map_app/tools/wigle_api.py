import configparser
import logging
import sqlite3
import requests
import random
from requests import ReadTimeout
from sqlalchemy import select, MetaData, Table, update
from src.map_app.tools import global_config_path
from src.map_app.source_core.db import get_db_connection, engine
from datetime import datetime

# TODO add more keys suport for bypass limits
def get_api_key():
    config = configparser.ConfigParser()
    config.read(global_config_path)
    api_keys = config['WIGLE']['api_keys'].split(',')
    return api_keys[0]

# table_name - in this table shoud be bssid, password,
def save_wigle_location(wigle_data, session, table, bssid, password):
    logging.info(wigle_data)
    if 'results' in wigle_data and len(wigle_data['results']) > 0:
        logging.info("results found")

        result = wigle_data['results'][0]
        essid = result.get('ssid')
        encryption = result.get('encryption')
        latitude = result.get('trilat')
        longitude = result.get('trilong')
        # network_type = "WIFI"
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
            logging.info(f"[WIGLE] Got error {e} when inserting entry for bssid: {bssid}")
            return False

    else:
        logging.info(f"❌ No geolocation for {bssid} found...")
        query = update(table).where(table.c.bssid == bssid).values(
            last_locate_try=datetime.now()
        )
        logging.info(query)
        session.execute(query)
        return False


def wigle_locate(table_name):
    localized_networks = total_networks = 0

    metadata = MetaData()
    table = Table(table_name, metadata, autoload_with=engine)

    with get_db_connection() as session:
        try:
            not_localized_q = select(table.c.bssid, table.c.password).distinct().where(
                (table.c.latitude.is_(None)) | (table.c.longitude.is_(None))
            ).order_by(table.c.last_locate_try.is_(None), table.c.last_locate_try)
            wpasec_data = session.execute(not_localized_q).fetchall()

            #TODO what limit ?
            #shuffle data to increase chance for hits for the next day when running into the API Limit
            random.shuffle(wpasec_data)
            api_key = get_api_key()
            logging.info(f"Wigle API key loaded, try check {len(wpasec_data)} networks")

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
                    logging.info(f"The Wigle API {api_key} Key is not authorized. Validate it in the Settings")
                    break
                elif response.status_code == 429:
                    logging.info("❌ Received status code 429: API Limit reached.")
                    break
                elif response.status_code == 200:
                    try:
                        wigle_data = response.json()
                        localized_networks += save_wigle_location(wigle_data, session, table, bssid, password)
                        session.commit() # update after eah request, because main limit is wigle API limit
                    except ValueError as e:
                        logging.info(f"Error parsing JSON response: {e}")
                        break
                else:
                    logging.info(f"Error retrieving data for {bssid}. Status code: {response.status_code}")
                    break
        except ReadTimeout as  e:
            logging.info(f"Timeout error: {e}")
    return localized_networks, total_networks


