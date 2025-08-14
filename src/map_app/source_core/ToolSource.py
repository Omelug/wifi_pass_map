import configparser
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

    @classmethod
    def clear_instances(cls):
        cls._instances.clear()

BASE_FILE = os.path.dirname(os.path.abspath(__file__))
sources_config_file = os.path.join(BASE_FILE,'..','sources','config')
os.makedirs(sources_config_file, exist_ok=True)

class ToolSource(metaclass=SingletonMeta):

    def __init__(self, source_name:str, config:Dict[str, Any]=None):
        super().__init__()
        self.SOURCE_NAME: str = source_name
        self.create_config(self.config_path(), config)

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        return None

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


class ToolGenerator():

    def __init__(self, tool_source:ToolSource, config_path=None):
        self.tool_params = dict()
        self.run_funs = dict()
        if config_path is None:
            self.config_path = tool_source.config_path()
        else:
            self.config_path = config_path

    def addParam(self, tool_name: str, param_name: str, input_type=str, validation_function=None, description="") -> None:
        if tool_name not in self.tool_params:
            self.tool_params[tool_name] = []
        config = configparser.ConfigParser()
        config.read(self.config_path)
        self.tool_params[tool_name].append((param_name, input_type, validation_function, config[tool_name][param_name],description))

    def add_run_fun(self, tool_name: str, run_fun) -> None:
        self.run_funs[tool_name] = run_fun

    def get_list(self):
        result = {}
        for tool_name, params in self.tool_params.items():
            entry = {"params": params}
            if tool_name in self.run_funs:
                entry["run_fun"] = self.run_funs[tool_name]
            result[tool_name] = entry
        return result


