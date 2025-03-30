import configparser
from map_app.source_core.Source import Source
from map_app.sources import config_path

def param_control(string):
    return string[0] == "e"


def print_example():
    print("Example text for debugging...")
    config = configparser.ConfigParser()
    config.read(config_path())
    custom_text = config['example_tool']['custom_text']
    print(f"{custom_text}")


class Example(Source):

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
