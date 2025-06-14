import configparser
import logging
import os
import subprocess
import sys
from pathlib import Path
import glob

from src.formator.bssid import extract_essid_bssid
from src.map_app.source_core.Table_v0 import Table_v0
from src.map_app.source_core.db import Database

sys.path.append(str(Path(__file__).resolve().parents[2]))

class Handshakes(Table_v0):
    __description__ = "MapSource for manipulation with raw handshake files"
    __requirement__ = ['hcxpcapngtool', "plugin:wigle"]

    def __init__(self):
        default_config = configparser.ConfigParser()
        default_config['handshake_scan'] = {
            'handshakes_dir' : 'data/raw/handshakes',
            'handshake_22000_file': 'data/raw/hash.hc22000',
        }
        super().__init__(type(self).__qualname__.lower(), default_config)

    # ------------FUNCTIONS----------------
    @staticmethod
    def __create_hash_file(config):
        HS_DIR = config['handshake_scan']['handshakes_dir']

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..'))
        file_22000 = config['handshake_scan']['handshake_22000_file']
        file_22000_path = os.path.abspath(os.path.join(base_dir, file_22000))

        logging.info(f"HANDSHAKE: Creating hash file {file_22000_path}")

        pcap_files = glob.glob(os.path.join(os.path.abspath(HS_DIR), '*.pcap'))
        hcxpcapngtool_cmd = ['hcxpcapngtool', '-o', file_22000_path] + pcap_files

        logging.debug(f"Executing: {' '.join(hcxpcapngtool_cmd)}")

        try:
            result = subprocess.run(hcxpcapngtool_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                if not os.access(file_22000_path, os.W_OK):
                    logging.error(f"No write permissions for directory '{file_22000_path}'. Cannot create '{file_22000_path}.")
            else:
                logging.info(f"Hash file created at {file_22000_path}")
        except Exception as e:
            logging.error(f"Failed to process files: {e}")


    def __load_hashes_to_db(self,config) -> None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..','..'))
        file_22000 = config['handshake_scan']['handshake_22000_file']
        file_22000_path = os.path.abspath(os.path.join(base_dir, file_22000))
        logging.info(f"{self.SOURCE_NAME}: Loading data from {file_22000_path} to database...")

        new_networks, duplicate_networks, invalid = 0, 0, 0

        if not os.path.exists(file_22000_path):
            logging.error(f"Hash file {file_22000_path} does not exist.")
            return

        with Database().get_db_connection() as session:
            with open(file_22000_path, 'r') as hash_file:
                for line in hash_file:
                    if line.startswith('WPA'):
                        essid, bssid = extract_essid_bssid(line)
                        if self._save_AP_to_db(
                                bssid=bssid,
                                essid=essid,
                                password=None,
                                session=session):
                            new_networks += 1
                        else:
                            duplicate_networks += 1
                    else:
                        invalid += 1
                        logging.error("Invalid handsake format")

        logging.info(
            f"Processed a total of {new_networks + duplicate_networks} networks, "
            f"{new_networks} new APs\n"
            f"{duplicate_networks} already known or duplicates\n"
            f"{invalid} invalid networks"
        )

    #-----------------------TOOLS FUNCTIONS-----------------------
    def __handshake_reload(self) -> None:
        config = configparser.ConfigParser()
        config.read(self.config_path())
        Handshakes.__create_hash_file(config)
        self.__load_hashes_to_db(config)


    def get_tools(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        hs_reload = [("hs_path", str, None, config['handshake_scan']['handshakes_dir'], "Path to the directory with handshakes"),]
        return {"handshake_reload": {"run_fun": self.__handshake_reload,
                                     "params":hs_reload},
                #"handshake_locate": {"run_fun": self.table_v0_locate}
                }
