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
