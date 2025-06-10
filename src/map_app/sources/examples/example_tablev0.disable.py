import configparser
import logging

from map_app.source_core.Table_v0 import Table_v0


class Example_Table_v0(Table_v0):
    __description__ = "example tablev0 source"
    def __init__(self):

        default_config = configparser.ConfigParser()
        default_config['example_tool'] = {
            'custom_text': 'example_string'
        }
        super().__init__("example_tablev0",config=default_config)

    def get_map_data(self, filters=None):

            pwned_data = [{
                    "bssid": "11:22:33:44:55:66",
                    "encryption": "WPA2",
                    "essid": "EXAMPLE_TALEv0",
                    "password": "pass",
                    "latitude": 31,
                    "longitude": -31
            }]
            return pwned_data
