import configparser
from abc import abstractmethod
from typing import Dict, Any, Optional

from map_app.source_core.ToolSource import ToolSource


class GlobalConfig(ToolSource):
    def __init__(self, source_name:str):
        default_config = configparser.ConfigParser()
        default_config['view_settings'] = {
            'ordered_sources': 'true',
        }
        super().__init__(source_name, default_config)
