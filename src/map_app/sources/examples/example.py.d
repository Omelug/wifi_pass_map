import configparser
import logging

from src.map_app.source_core.Source import MapSource

def param_control(string):
    return string[0] == "e"

class Example(MapSource):
    __description__ = "example source  - check for dicumentation"
    def __init__(self):

        default_config = configparser.ConfigParser()
        default_config['example_tool'] = {
            'custom_text': 'example_string'
        }
        super().__init__("example",config=default_config)

    def __print_example(self):
        logging.info("Example text for debugging...")
        config = configparser.ConfigParser()
        config.read(self.config_path())
        custom_text = config['example_tool']['custom_text']
        logging.info(f"{custom_text}")

    def get_tools(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())

        params = [("custom_text", str, param_control, config['example_tool']['custom_text'], "custom text for print")]
        return {"example_tool": {"run_fun":  self.__print_example, "params":params}}

    def get_map_data(self, filters=None):

            pwned_data = [{
                    "bssid": "11:22:33:44:55:66",
                    "encryption": "WPA2",
                    "essid": "EXAMPLE",
                    "password": "pass",
                    "latitude": 30,
                    "longitude": -30
            }]
            return pwned_data
