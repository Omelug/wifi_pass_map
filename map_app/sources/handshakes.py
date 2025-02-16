import configparser
import os
import subprocess
import sys

from sqlalchemy import Table, inspect
from sqlalchemy.exc import IntegrityError

from formator.bssid import extract_essid_bssid
from map_app.sources import sources
from map_app.sources.sources import config_path
from map_app.tools.db import create_wifi_table, Base, Session
from map_app.tools.wigle_api import wigle_locate

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from map_app.tools.db import engine,metadata

__description__ = "Source for manipulation with raw handshake files"


TABLE_NAME = 'handshakes'
if TABLE_NAME in metadata.tables:
    table = metadata.tables[TABLE_NAME]
else:
    if not inspect(engine).has_table(TABLE_NAME):
        table = create_wifi_table(TABLE_NAME)
        metadata.create_all(engine)
    else:
        table = Table(TABLE_NAME, metadata, autoload_with=engine)


class Handshake(Base):
    __tablename__ = TABLE_NAME
    __table__ = table

# ------------CONFIG----------------
if not os.path.exists(config_path()):
    config = configparser.ConfigParser()
    config['handshake_scan'] = {
        'rescan_days': '7',
        'handshakes_dir' : 'data/raw/handshakes',
        'handshake_22000_file': 'data/raw/hash.hc22000',
    }

    with open(config_path(), 'w') as config_file:
        config.write(config_file)

    print(f"Handsakes configuration created {config_path()}")
    #TODO maybe database of tried discts and table to tried discts

# ------------FUNCTIONS----------------

def get_map_data(filters=None):
    return sources.get_map_data(TABLE_NAME, filters)


def create_hash_file(config):
    HS_DIR = config['handshake_scan']['handshakes_dir']
    FILE_22000 = config['handshake_scan']['handshake_22000_file']

    print(f"HANDSHAKE: Creating hash file {FILE_22000}")

    command = ['hcxpcapngtool', '-o', os.path.abspath(FILE_22000), os.path.join(os.path.abspath(HS_DIR), '*.pcap')]
    print(f"Executing: {' '.join(command)}")

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error processing files: {result.returncode} {result.stderr}")
        else:
            print(f"Hash file created at {FILE_22000}")
    except Exception as e:
        print(f"Failed to process files: {e}")

def load_hashes_to_db(config):
    FILE_22000 = config['handshake_scan']['handshake_22000_file']
    print(f"HANDSHAKE: Loading data from {FILE_22000} to database...")
    new_handshakes = 0

    if not os.path.exists(FILE_22000):
        print(f"Hash file {FILE_22000} does not exist.")
        return

    with open(FILE_22000, 'r') as hash_file:
        for line in hash_file:
            if line.startswith('WPA'):

                essid, bssid = extract_essid_bssid(line)

                password = None  # TODO Extract password if available

                with Session() as session:
                    try:
                        new_handshake_entry = Handshake(
                            bssid=bssid,
                            essid=essid,
                            password=password
                        )
                        session.add(new_handshake_entry)
                        session.commit()
                        new_handshakes += 1
                    except IntegrityError:
                        session.rollback()
                        #print(f"Duplicate entry for {bssid} - {essid}")
    print(f"Handshakes loading done, {new_handshakes} new handshakes added")


#-----------------------TOOLS FUNCTIONS-----------------------

def handshake_reload():
    config = configparser.ConfigParser()
    config.read(config_path())

    create_hash_file(config)
    load_hashes_to_db(config)

def handshake_locate():
    print("HANDSHAKE: Starting data localization")
    localized_networks, total_networks = wigle_locate(TABLE_NAME)
    print(f"HANDSHAKE: Located {localized_networks} out of {total_networks} networks")

def get_tools():
    config = configparser.ConfigParser()
    config.read(config_path())
    return {"handshake_reload": {"run_fun": handshake_reload},"handshake_locate": {"run_fun": handshake_locate}}
