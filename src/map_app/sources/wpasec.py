import configparser
import csv
import logging
import os
import sys
import requests
from src.map_app.source_core.Table_v0 import Table_v0
from src.map_app.source_core.db import Database

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Wpasec(Table_v0):
    __description__ = "Source to get potfile from wpasec (https://github.com/RealEnder/dwpa)"

    def __init__(self):

        default_config = configparser.ConfigParser()
        default_config['wpasec_update'] = {
            'api_keys': '<your_wpasec_api_key_here>',
            'wpasec_link': 'https://wpa-sec.stanev.org'
        }
        super().__init__(table_name=type(self).__qualname__.lower(),config=default_config)

    # ------------FUNCTIONS----------------

    # Return the CSV content for further processing
    @staticmethod
    def __download_potfile(config,api_key) -> bytes|None:
        api_url = config['wpasec_update']['wpasec_link'] + "/?api&dl=1"
        cookies = {'key': api_key}
        try:
            return requests.get(api_url, cookies=cookies).content
        except requests.RequestException as e:
            raise Exception(f"HTTP Error: {e}")

    #-----------------------TOOLS FUNCTIONS-----------------------
    #Save csv content to wpasec table in database
    def __csv_to_db(self,csv_content):
        new_networks, duplicate_networks, invalid = 0,0,0
        csv_reader = csv.reader(csv_content.decode('utf-8').splitlines(), delimiter=':')

        with Database().get_db_connection() as session:
            for row in csv_reader:
                if len(row) == 4:
                    bssid, _, essid, password = row
                    if not self._new_row(bssid):
                        continue
                    result = self._save_AP_to_db(
                        bssid, essid, password, bssid_format=True, session=session
                    )
                    if result:
                        new_networks += 1
                    else:
                        duplicate_networks += 1
                else:
                    invalid += 1
                    logging.error(f"Cant parse line in wpasec potfile: {row}")

        logging.info(
                f"Processed a total of {new_networks+duplicate_networks} networks, "
              f"{new_networks} new APs\n"
              f"{duplicate_networks} already known or duplicates\n"
              f"{invalid} invalid networks"
        )

    def __get_wpasec_key(self) -> str:
        config = configparser.ConfigParser()
        config.read(self.config_path())
        return config['wpasec_update']['api_keys'].split(',')[0]

    #update data from wpa_sec
    def __wpasec_update(self) -> None:
        logging.info(f"{self.SOURCE_NAME}: Starting data update")
        config = configparser.ConfigParser()
        config.read(self.config_path())

        api_key = self.__get_wpasec_key()
        acc_potfile = self.__download_potfile(config,api_key)
        self.__csv_to_db(acc_potfile)

    def get_tools(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())

        wpasec_update_params = [("api_keys", str, None, config['wpasec_update']['api_keys'], "Key for WPASEC"),
                                ("wpasec_link", str, None, config['wpasec_update']['wpasec_link'], "Link to wpasec api")]
        return {"wpasec_update":  {"run_fun": self.__wpasec_update, "params":wpasec_update_params}}
