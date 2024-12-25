# ------------CONFIG----------------
import configparser
import os

# create default config if not exists
TOOLS_CONFIG_FILE = "map_app/tools"
config_file_path = f'{TOOLS_CONFIG_FILE}/tool_parts_config.ini'
if not os.path.exists(config_file_path):
    config = configparser.ConfigParser()

    config['WIGLE'] = {'api_keys': 'your_wpasec_api_key_here'}

    with open(config_file_path, 'w') as config_file:
        config.write(config_file)
    print(f"{os.path.basename(__file__)} configuration created {config_file_path}")