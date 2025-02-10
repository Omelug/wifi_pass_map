import configparser
import os
from map_app.sources.sources import config_path

# ------------CONFIG----------------

if not os.path.exists(config_path()):
    config = configparser.ConfigParser()

    # EXAMPLE_CONFIG update
    config['example_tool'] = {
        'custom_text': 'example_string'
    }

    with open(config_path(), 'w') as config_file:
        config.write(config_file)
    print(f"example configuration created {config_path()}")

def get_map_data(filters=None):

        pwned_data = [
            {
                "bssid": "11:22:33:44:55:66",
                "encryption": "WPA2",
                "essid": "EXAMPLE",
                "password": "pass",
                "latitude": 0,
                "longitude": 0
            }
        ]
        return pwned_data

#-----------------------TOOLS FUNCTIONS-----------------------

def print_example():
    print("Example text for debugging...")
    config = configparser.ConfigParser()
    config.read(config_path())
    custom_text = config['example_tool']['custom_text']
    print(f"{custom_text}")

def param_control(string):
    return string[0] == "e"

def get_tools():
    config = configparser.ConfigParser()
    config.read(config_path())

    params = [("custom_text",str,param_control,config['example_tool']['custom_text'],"custom text for print")]
    return {"example_tool": {"run_fun":print_example, "params":params}}
