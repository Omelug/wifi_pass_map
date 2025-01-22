import csv
import datetime
import os
import sys
from select import select

import requests
from sqlalchemy import Column, String, UniqueConstraint, Table, inspect, MetaData
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import DDL
from sqlalchemy import event
import configparser

from sqlalchemy.sql import expression

from map_app.tools.db import Base, get_db_connection, create_wifi_table

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from formator.bssid import format_bssid
from map_app.tools.db import Session,engine,metadata
from map_app.tools.wigle_api import wigle_locate

TABLE_NAME = 'wpasec'
if not inspect(engine).has_table(TABLE_NAME):
    wpasec_table = create_wifi_table(TABLE_NAME)
    metadata.create_all(engine)
else:
    wpasec_table = Table(TABLE_NAME, metadata, autoload_with=engine)

class Wpasec(Base):
    __table__ = wpasec_table

# ------------CONFIG----------------

# create default config if not exists
BASE_FILE = os.path.dirname(os.path.abspath(__file__))
SOURCES_CONFIG_FILE = os.path.join(BASE_FILE,'..','sources','config')
os.makedirs(SOURCES_CONFIG_FILE, exist_ok=True)

config_file_path = f'{SOURCES_CONFIG_FILE}/wpasec.ini'

print(f"WPASEC: Config file path: {config_file_path}")

if not os.path.exists(config_file_path):
    config = configparser.ConfigParser()
    # WPASEC update
    config['WPASEC_UPDATE'] = {
        'api_keys': '<your_wpasec_api_key_here>',
        'wpasec_link':'https://wpa-sec.stanev.org'
    }

    with open(config_file_path, 'w') as config_file:
        config.write(config_file)
    print(f"WPASEC configuration created {config_file_path}")

# ------------SAVE_NETWORK----------------
def save_network_wpasec(wpasec_row) -> bool: #added new ?
    """
    Save network to wpasec table in database
    """
    bssid, _, essid, password = wpasec_row

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
            print(f"New network: {essid}")
            return True
        except IntegrityError:
            session.rollback()
            return False

def csv_to_db(csv_content):
    """
    Save csv content to wpasec table in database
    """
    new_networks, duplicate_networks = 0,0

    csv_reader = csv.reader(csv_content.decode('utf-8').splitlines(), delimiter=':')

    for row in csv_reader:
        if len(row) == 4:
            if save_network_wpasec(row):
                new_networks += 1
            else:
                duplicate_networks += 1
        else:
            raise ValueError(f"Invalid CSV row lenght: {row}")

    print(f"Processed a total of {new_networks+duplicate_networks} networks, "
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

def get_map_data(filters=None):
    with get_db_connection() as session:
        metadata = MetaData()
        table = Table(TABLE_NAME, metadata, autoload_with=engine)

        query = expression.select(
            table.c.bssid,
            table.c.encryption,
            table.c.essid,
            table.c.password,
            table.c.latitude,
            table.c.longitude
        ).distinct().where(
            (table.c.latitude.is_not(None)) | (table.c.longitude.is_not(None))
        )

        if filters:
            for key, value in filters.items():
                if hasattr(table.c, key):
                    query = query.where(getattr(table.c, key) == value)
                else:
                    print(f"Column {key} does not exist in the table")
        #print(query)
        #compiled_query = query.compile(engine, compile_kwargs={"literal_binds": True})
        #print(str(compiled_query))
        wpasec_data = session.execute(query).fetchall()

        pwned_data = [
            {
                "bssid": row.bssid,
                "encryption": row.encryption,
                "essid": row.essid,
                "password": row.password,
                "latitude": row.latitude,
                "longitude": row.longitude
            }
            for row in wpasec_data
        ]
        return pwned_data

def get_wpasec_key():
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config['WPASEC_UPDATE']['api_keys'].split(',')[0]

#update data from wp_sec
def wpasec_update():
    print("WPASEC: Starting data update")
    config = configparser.ConfigParser()
    config.read(config_file_path)

    api_key = get_wpasec_key()
    acc_potfile = download_potfile(config,api_key)
    csv_to_db(acc_potfile)

def wpasec_locate():
    print("WPASEC: Starting data localization")
    localized_networks, total_networks = wigle_locate("wpasec")
    print(f"WPASEC: Located {localized_networks} out of {total_networks} networks")


def get_tools():
    return {"wpasec_update": wpasec_update, "wpasec_locate": wpasec_locate}

if __name__ == "__main__":
    wpasec_update(sys.argv[1])
