# ------------CONFIG----------------
import configparser
import logging
import os

# create default config if not exists
TOOLS_CONFIG_FILE = os.path.join(os.path.dirname(__file__))
global_config_path = f'{TOOLS_CONFIG_FILE}/tools_keys.ini'
# TODO add special params for tools not in sources
if not os.path.exists(global_config_path):
    config = configparser.ConfigParser()

    config['WIGLE'] = {'api_keys': 'your_wpasec_api_key_here'}

    with open(global_config_path, 'w') as config_file:
        config.write(config_file)
    logging.info(f"{os.path.basename(__file__)} configuration created {global_config_path}")