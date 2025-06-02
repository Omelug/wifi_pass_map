import configparser
from src.map_app.source_core.Source import Source
from src.map_app.sources import config_path
import logging

def param_control(string):
    return string[0] == "e"


def print_example():
    logging.info("Example text for debugging...")
    config = configparser.ConfigParser()
    config.read(config_path())
    custom_text = config['example_tool']['custom_text']
    logging.info(f"{custom_text}")


class Example(MapSource):
    __description__ = "example source "
    def __init__(self):

        default_config = configparser.ConfigParser()
        default_config['example_tool'] = {
            'custom_text': 'example_string'
        }
        super().__init__(default_config)

    def get_tools(self):
        config = configparser.ConfigParser()
        config.read(config_path())

        params = [("custom_text", str, param_control, config['example_tool']['custom_text'], "custom text for print")]
        return {"example_tool": {"run_fun": print_example, "params":params}}

    def get_map_data(self, filters=None):

            pwned_data = [{
                    "bssid": "11:22:33:44:55:66",
                    "encryption": "WPA2",
                    "essid": "EXAMPLE",
                    "password": "pass",
                    "latitude": 0,
                    "longitude": 0
            }]
            return pwned_data
