import configparser
from typing import Dict, Any

from map_app.source_core.ToolSource import ToolSource


class GlobalConfig(ToolSource):
    def __init__(self):
        default_config = configparser.ConfigParser()
        default_config['view_settings'] = {
            'ordered_sources': '',
        }
        super().__init__(type(self).__qualname__.lower(), default_config)


    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        config = configparser.ConfigParser()
        config.read(self.config_path())

        global_param = [("ordered_sources", str, None, config['view_settings']['ordered_sources'], "Ordered listof sources"), ]
        return {
            "Global Settings": {"params": global_param},
        }

    def get_ordered_sources(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        ordered = config.get('view_settings', 'ordered_sources', fallback='')
        return [s for s in ordered.split(',') if s]

    def save_ordered_sources(self, order_list):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        if 'view_settings' not in config:
            config['view_settings'] = {}
        config['view_settings']['ordered_sources'] = ','.join(order_list)
        with open(self.config_path(), 'w') as f:
            config.write(f)