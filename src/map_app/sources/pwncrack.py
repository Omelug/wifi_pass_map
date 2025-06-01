import configparser
import csv
import logging
import os
import sys
import requests
from src.map_app.source_core.Table_v0 import Table_v0
from src.map_app.sources import config_path
from src.map_app.source_core.db import get_db_connection
from src.formator.potfile import decode_hexed

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Pwncrack(Table_v0):
    __description__ = "Source to get potfile from pwncrack (https://github.com/Terminatoror/pwncrack-backend)"

    TABLE_NAME = __qualname__.lower()

    def __init__(self):

        default_config = configparser.ConfigParser()
        default_config['pwncrack_update'] = {
            'api_keys': '<your_pwncrack_api_key_here>',
            'pwncrack_link': 'https://pwncrack.org/'
        }
        super().__init__(self.TABLE_NAME, default_config)

    # ------------FUNCTIONS----------------


    @staticmethod
    def __download_potfile(config,api_key):
        api_url = config['pwncrack_update']['pwncrack_link'] + "/download_potfile?key=" + api_key
        try:
            return requests.get(api_url).content
        except requests.RequestException as e:
            raise Exception(f"HTTP Error: {e}")

    #-----------------------TOOLS FUNCTIONS-----------------------
    #Save csv content to pwncrack table in database
    def __csv_to_db(self,csv_content):
        #TODO Hex input!
        new_networks, duplicate_networks = 0,0
        csv_reader = csv.reader(csv_content.decode('utf-8').splitlines(), delimiter=':')

        with get_db_connection() as session:
            for row in csv_reader:
                if len(row) == 5:
                    _, bssid, _, essid, password = row
                    essid = decode_hexed(essid)
                    password = decode_hexed(password)
                    result = self._save_AP_to_db(
                        bssid, essid,password, bssid_format=True, session=session
                    )
                    if result:
                        new_networks += 1
                    else:
                        duplicate_networks += 1
                else:
                    logging.error(f"Cantparse line in potfile: {row}")

        logging.info(f"Processed a total of {new_networks+duplicate_networks} networks: "
              f"{new_networks} new APs,"
              f"{duplicate_networks} already known or duplicates")


    @staticmethod
    def __get_pwncrack_key():
        config = configparser.ConfigParser()
        config.read(config_path())
        return config['pwncrack_update']['api_keys'].split(',')[0]

    #update data from pwncrack
    def __pwncrack_update(self):
        logging.info(f"{self.TABLE_NAME}: Starting data update")
        config = configparser.ConfigParser()
        config.read(config_path())

        api_key = Pwncrack.__get_pwncrack_key()
        acc_potfile = Pwncrack.__download_potfile(config,api_key)
        self.__csv_to_db(acc_potfile)

    def get_tools(self):
        config = configparser.ConfigParser()
        config.read(config_path())

        pwncrack_update_params = [("api_keys", str, None, config['pwncrack_update']['api_keys'], "Key for pwncrack"),
                                ("pwncrack_link", str, None, config['pwncrack_update']['pwncrack_link'], "Link to pwncrack api")]
        return {"pwncrack_update":  {"run_fun": self.__pwncrack_update, "params":pwncrack_update_params},
                "pwncrack_locate":  {"run_fun": self.table_v0_locate}}
