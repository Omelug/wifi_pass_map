import configparser
import logging

from map_app.source_core.ToolSource import ToolGenerator
from src.map_app.source_core.Source import MapSource

def param_control(string):
    return string[0] == "e"

class Example(MapSource):
    __description__ = "example source  - check for dicumentation"
    __requirements__ = None

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
        gen = ToolGenerator(self)
        gen.addParam(tool_name="example_tool", param_name="custom_text", validation_function=param_control,
                     description="custom text for print")
        gen.add_run_fun("example_tool", self.__print_example)
        return gen.get_list()

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
