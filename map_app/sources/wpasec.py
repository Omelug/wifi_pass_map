import csv
import datetime
import os
import sys
import requests
from sqlalchemy import Column, String, UniqueConstraint, Table, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import DDL
from sqlalchemy import event
import configparser
from map_app.tools.db import Base, get_db_connection, create_wifi_table

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from formator.bssid import format_bssid
from map_app.tools.db import Session,engine,metadata
from map_app.tools.wigle_api import wigle_locate

wpasec_table = create_wifi_table('wpasec')
class Wpasec(Base):
    __table__ = wpasec_table

metadata.create_all(engine)


# ------------CONFIG----------------

# create default config if not exists
SOURCES_CONFIG_FILE = "map_app/sources/config"
os.makedirs(SOURCES_CONFIG_FILE, exist_ok=True)
config_file_path = f'{SOURCES_CONFIG_FILE}/wpasec.ini'
if not os.path.exists(config_file_path):
    config = configparser.ConfigParser()
    # WPASEC update
    config['WPASEC_UPDATE'] = {'api_keys': '<your_wpasec_api_key_here>',
                            'wpasec_link':'https://wpa-sec.stanev.org'
                            }

    with open(config_file_path, 'w') as config_file:
        config.write(config_file)
    print(f"WPASEC configuration created {config_file_path}")

def csv_to_db(csv_content):
    total_networks = 0
    new_networks = 0
    duplicate_networks = 0

    csv_reader = csv.reader(csv_content.decode('utf-8').splitlines(), delimiter=':')

    for row in csv_reader:
        if len(row) == 4:
            total_networks += 1
            bssid, sta_mac, essid, password = row

            with Session() as session:
                try:

                    new_wpasec_entry = Wpasec(
                        bssid=format_bssid(bssid),
                        essid=essid,
                        password=password,
                        time=None
                    )
                    session.add(new_wpasec_entry)
                    session.commit()

                    new_networks += 1
                    print(f"New network: {essid}")
                except IntegrityError:
                    session.rollback()
                    duplicate_networks += 1
        else:
            raise ValueError(f"Invalid CSV row: {row}")

    print(f"Processed a total of {total_networks} networks, "
          f"{new_networks} new APs,"
          f"{duplicate_networks} already known or duplicates")

# Return the CSV content for further processing
def download_potfile(config,api_key):
    api_url = config['WPASEC_UPDATE']['wpasec_link'] + "/?api&dl=1"
    cookies = {'key': api_key}
    try:
        response = requests.get(api_url, cookies=cookies)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP Error: {e}")

def get_map_data():
    with get_db_connection() as conn:
        cursor = conn.connection.cursor()

        cursor.execute(f'SELECT DISTINCT bssid, essid, password, latitude, longitude FROM wpasec '
                       f'WHERE latitude IS NULL OR longitude IS NULL')
        wpasec_data = cursor.fetchall()

        pwned_data = [
            {
                "bssid": row[0],
                "essid": row[1],
                "password": row[2],
                "latitude": row[3],
                "longitude": row[4]
            }
            for row in wpasec_data
        ]
        return pwned_data

#update data from wp_sec
def wpasec_update():
    print("WPASEC: Starting data update")
    config = configparser.ConfigParser()
    config.read(config_file_path)
    api_keys = config['WPASEC_UPDATE']['api_keys'].split(',')
    for api_key in api_keys:
        acc_potfile = download_potfile(config,api_key)
        csv_to_db(acc_potfile)

def wpasec_locate():
    print("WPASEC: Starting data localization")
    wigle_locate("wpasec")


def get_tools():
    return {"wpasec_update": wpasec_update, "wpasec_locate": wpasec_locate}

if __name__ == "__main__":
    wpasec_update(sys.argv[1])
