import configparser
import csv
import os
import sys

import requests
from sqlalchemy import Table, inspect
from sqlalchemy.exc import IntegrityError
from map_app.sources import sources
from map_app.sources.sources import config_path
from map_app.tools.db import Base, create_wifi_table

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from formator.bssid import format_bssid
from map_app.tools.db import Session,engine,metadata
from map_app.tools.wigle_api import wigle_locate

TABLE_NAME = 'wpasec'

# Check if the table already exists in metadata

if TABLE_NAME in metadata.tables:
    table = metadata.tables[TABLE_NAME]
else:
    if not inspect(engine).has_table(TABLE_NAME):
        table = create_wifi_table(TABLE_NAME)
        metadata.create_all(engine)
    else:
        table = Table(TABLE_NAME, metadata, autoload_with=engine)

if TABLE_NAME not in Base.metadata.tables:
    class Wpasec(Base):
        __tablename__ = TABLE_NAME
        __table__ = table

# ------------CONFIG----------------

#default config values
if not os.path.exists(config_path()):
    config = configparser.ConfigParser()

    config['wpasec_update'] = {
        'api_keys': '<your_wpasec_api_key_here>',
        'wpasec_link':'https://wpa-sec.stanev.org'
    }

    with open(config_path(), 'w') as config_file:
        config.write(config_file)

    print(f"WPASEC configuration created {config_path()}")


# ------------FUNCTIONS----------------

def get_map_data(filters=None):
    return sources.get_map_data(TABLE_NAME,filters)

def get_wpasec_key():
    config = configparser.ConfigParser()
    config.read(config_path())
    return config['wpasec_update']['api_keys'].split(',')[0]

# Return the CSV content for further processing
def download_potfile(config,api_key):
    api_url = config['wpasec_update']['wpasec_link'] + "/?api&dl=1"
    cookies = {'key': api_key}
    try:
        response = requests.get(api_url, cookies=cookies)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP Error: {e}")

#Save network to wpasec table in database
def save_network_wpasec(wpasec_row) -> bool: #added new ?
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

#Save csv content to wpasec table in database
def csv_to_db(csv_content):
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

#-----------------------TOOLS FUNCTIONS-----------------------

#update data from wpa_sec
def wpasec_update():
    print("WPASEC: Starting data update")
    config = configparser.ConfigParser()
    config.read(config_path())

    api_key = get_wpasec_key()
    acc_potfile = download_potfile(config,api_key)
    csv_to_db(acc_potfile)

def wpasec_locate():
    print("WPASEC: Starting data localization")
    localized_networks, total_networks = wigle_locate(TABLE_NAME)
    print(f"WPASEC: Located {localized_networks} out of {total_networks} networks")


def get_tools():
    config = configparser.ConfigParser()
    config.read(config_path())

    wpasec_update_params = [("api_keys", str, None, config['wpasec_update']['api_keys'], "Key for WPASEC"),
                            ("wpasec_link", str, None, config['wpasec_update']['wpasec_link'], "Link to wpasec api")]
    return {"wpasec_update":  {"run_fun":wpasec_update, "params":wpasec_update_params},
            "wpasec_locate":  {"run_fun":wpasec_locate}}

# only for testing purposes, not called by the app
if __name__ == "__main__":
    wpasec_update(sys.argv[1])
