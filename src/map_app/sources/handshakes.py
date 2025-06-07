import configparser
import logging
import os
import subprocess
import sys
from pathlib import Path
import glob

from src.formator.bssid import extract_essid_bssid
from src.map_app.source_core.Table_v0 import Table_v0
from src.map_app.source_core.db import get_db_connection

sys.path.append(str(Path(__file__).resolve().parents[2]))

class Handshakes(Table_v0):
    __description__ = "MapSource for manipulation with raw handshake files"
    __requirement__ = ['hcxpcapngtool', "plugin:wigle"]
    TABLE_NAME = __qualname__.lower()

    def __init__(self):
        default_config = configparser.ConfigParser()
        default_config['handshake_scan'] = {
            'rescan_days': '7',
            'handshakes_dir' : 'data/raw/handshakes',
            'handshake_22000_file': 'data/raw/hash.hc22000',
        }
        super().__init__(self.TABLE_NAME, default_config)

    # ------------FUNCTIONS----------------
    @staticmethod
    def __create_hash_file(config):
        HS_DIR = config['handshake_scan']['handshakes_dir']
        FILE_22000 = config['handshake_scan']['handshake_22000_file']

        logging.info(f"HANDSHAKE: Creating hash file {FILE_22000}")

        pcap_files = glob.glob(os.path.join(os.path.abspath(HS_DIR), '*.pcap'))
        hcxpcapngtool_cmd = ['hcxpcapngtool', '-o', os.path.abspath(FILE_22000)] + pcap_files

        logging.debug(f"Executing: {' '.join(hcxpcapngtool_cmd)}")

        try:
            result = subprocess.run(hcxpcapngtool_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                parent_dir = os.path.dirname(os.path.abspath(FILE_22000))
                if not os.access(parent_dir, os.W_OK):
                    logging.error(f"No write permissions for directory '{parent_dir}'. Cannot create '{os.path.dirname(os.path.abspath(FILE_22000))}.")
            else:
                logging.info(f"Hash file created at {FILE_22000}")
        except Exception as e:
            logging.error(f"Failed to process files: {e}")


    def __load_hashes_to_db(self,config) -> None:
        FILE_22000 = config['handshake_scan']['handshake_22000_file']
        logging.info(f"{self.SOURCE_NAME}: Loading data from {FILE_22000} to database...")
        new_handshakes = 0

        if not os.path.exists(FILE_22000):
            logging.error(f"Hash file {FILE_22000} does not exist.")
            return

        with open(FILE_22000, 'r') as hash_file:
            for line in hash_file:
                if line.startswith('WPA'):
                    essid, bssid= extract_essid_bssid(line)
                    if self._new_row(bssid):
                        continue
                    with get_db_connection() as session:
                        if self._save_AP_to_db(bssid, essid, None, session=session):
                            new_handshakes += 1
                else:
                    logging.error("Invalid handsake format")
        logging.info(f"{self.SOURCE_NAME}: loading done, {new_handshakes} new handshakes added")


    #-----------------------TOOLS FUNCTIONS-----------------------
    def __handshake_reload(self) -> None:
        config = configparser.ConfigParser()
        config.read(self.config_path())
        Handshakes.__create_hash_file(config)
        self.__load_hashes_to_db(config)


    def get_tools(self):
        super().get_tools()
        config = configparser.ConfigParser()
        config.read(self.config_path())
        hs_reload = [("hs_path", str, None, config['handshake_scan']['handshakes_dir'], "Path to the directory with handshakes"),]
        return {"handshake_reload": {"run_fun": self.__handshake_reload,
                                     "params":hs_reload},
                #"handshake_locate": {"run_fun": self.table_v0_locate}
                }
