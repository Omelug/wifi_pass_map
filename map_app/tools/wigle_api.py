import configparser
import sqlite3
import sys
import requests
import random

from requests import ReadTimeout

from map_app.tools import config_file_path
from map_app.tools.db import get_db_connection


# TODO add more keys suport for bypass limits
def get_api_key():
    config = configparser.ConfigParser()
    config.read(config_file_path)
    api_keys = config['WIGLE']['api_keys'].split(',')
    return api_keys[0]

# table_name - in this table shoud be bssid, password,
def wigle_locate(table_name):
    new_networks = no_geolocation_networks = total_networks = 0

    with get_db_connection() as conn:
        cursor = conn.connection.cursor()
        try:
            cursor.execute(f'SELECT DISTINCT bssid, password FROM {table_name} '
                           f'WHERE latitude IS NULL OR longitude IS NULL')
            wpasec_data = cursor.fetchall()

            #TODO what limit ?
            #shuffle data to increase chance for hits for the next day when running into the API Limit
            random.shuffle(wpasec_data)
            api_key = get_api_key()
            print(f"Wigle API key loaded, try check {len(wpasec_data)} networks")

            for row in wpasec_data:
                bssid, password = row

                total_networks += 1

                response = requests.get(
                    f"https://api.wigle.net/api/v2/network/search?netid={bssid}",
                    headers={"Authorization": f"Basic {api_key}"},
                    timeout=5
                )

                if response.status_code == 401:
                    print(f"The Wigle API {api_key} Key is not authorized. Validate it in the Settings")
                    break
                elif response.status_code == 429:
                    print("❌ Received status code 429: API Limit reached.")
                    break
                elif response.status_code == 200:
                    wigle_data = response.json()
                    print(wigle_data)
                    if 'results' in wigle_data and len(wigle_data['results']) > 0:
                        result = wigle_data['results'][0]
                        essid = result.get('ssid')
                        encryption = result.get('encryption')
                        latitude = result.get('trilat')
                        longitude = result.get('trilong')
                        #network_type = "WIFI"
                        time = result.get('lasttime')

                        print(f"✅📌 Found geolocation for {essid}({bssid}).")
                        try:
                            cursor.execute(f'''
                                UPDATE {table_name}
                                SET encryption = ?, latitude = ?, longitude = ?, time = ?,essid = ?
                                WHERE bssid = ?
                            ''', (encryption, latitude, longitude, time, essid, bssid))
                            new_networks += 1
                        except sqlite3.Error as e:
                            print(f"[WIGLE] Got error {e} when inserting entry for network_id: {bssid}")

                    else:
                        no_geolocation_networks += 1
                        print(f"❌ No geolocation for {bssid} found...")
                else:
                    print(f"Error retrieving data for {bssid}. Status code: {response.status_code}")
                    break
        except ReadTimeout as  e:
            print(f"Timeout error: {e}")
        finally:
            conn.commit()

    return new_networks, no_geolocation_networks, total_networks


