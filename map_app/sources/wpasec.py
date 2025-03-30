import configparser
import csv
import os
import sys
import requests
from map_app.source_core.Table_v0 import Table_v0
from map_app.sources import config_path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Wpasec(Table_v0):
    TABLE_NAME = 'wpasec'

    def __init__(self):

        default_config = configparser.ConfigParser()
        default_config['wpasec_update'] = {
            'api_keys': '<your_wpasec_api_key_here>',
            'wpasec_link': 'https://wpa-sec.stanev.org'
        }
        super().__init__(self.TABLE_NAME, default_config)


    # ------------FUNCTIONS----------------

    # Return the CSV content for further processing
    @staticmethod
    def __download_potfile(config,api_key):
        api_url = config['wpasec_update']['wpasec_link'] + "/?api&dl=1"
        cookies = {'key': api_key}
        try:
            response = requests.get(api_url, cookies=cookies)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP Error: {e}")

    #-----------------------TOOLS FUNCTIONS-----------------------
    #Save csv content to wpasec table in database
    def __csv_to_db(self,csv_content):
        new_networks, duplicate_networks = 0,0

        csv_reader = csv.reader(csv_content.decode('utf-8').splitlines(), delimiter=':')

        for row in csv_reader:
            if len(row) == 4:
                bssid, _, essid, password = row
                if self._save_AP_to_db(bssid, essid,password):
                    new_networks += 1
                else:
                    duplicate_networks += 1
            else:
                raise ValueError(f"Invalid CSV row lenght: {row}")

        print(f"Processed a total of {new_networks+duplicate_networks} networks, "
              f"{new_networks} new APs,"
              f"{duplicate_networks} already known or duplicates")


    @staticmethod
    def __get_wpasec_key():
        config = configparser.ConfigParser()
        config.read(config_path())
        return config['wpasec_update']['api_keys'].split(',')[0]

    #update data from wpa_sec
    def __wpasec_update(self):
        print("WPASEC: Starting data update")
        config = configparser.ConfigParser()
        config.read(config_path())

        api_key = Wpasec.__get_wpasec_key()
        acc_potfile = Wpasec.__download_potfile(config,api_key)
        self.__csv_to_db(acc_potfile)

    def get_tools(self):
        config = configparser.ConfigParser()
        config.read(config_path())

        wpasec_update_params = [("api_keys", str, None, config['wpasec_update']['api_keys'], "Key for WPASEC"),
                                ("wpasec_link", str, None, config['wpasec_update']['wpasec_link'], "Link to wpasec api")]
        return {"wpasec_update":  {"run_fun": self.__wpasec_update, "params":wpasec_update_params},
                "table_v0_locate":  {"run_fun": self.table_v0_locate}}

