import inspect
import logging
import os
from typing import Dict, Any

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

BASE_FILE = os.path.dirname(os.path.abspath(__file__))
sources_config_file = os.path.join(BASE_FILE,'..','sources','config')
os.makedirs(sources_config_file, exist_ok=True)

class ToolSource(metaclass=SingletonMeta):

    def __init__(self, source_name:str, config:Dict[str, Any]=None):
        super().__init__()
        self.SOURCE_NAME: str = source_name
        self.create_config(self.config_path(), config)

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        return {}

    def create_config(self, conf_path:str=None, config=None) -> None:
        if config is None:
            return
        if conf_path is None:
            conf_path = self.config_path()
        if not os.path.exists(conf_path):
            with open(conf_path, 'w') as config_file:
                config.write(config_file)
            logging.info(f"{self.SOURCE_NAME} configuration created {conf_path}")

    def config_path(self, config_name = None) -> str:
        if config_name is None:
            config_name = self.SOURCE_NAME
        if config_name is None:
            frame = inspect.stack()[1]
            calling_script = frame[1]
            config_name = os.path.splitext(os.path.basename(calling_script))[0]
        return f'{sources_config_file}/{config_name}.ini'


