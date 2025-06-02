from typing import Dict, Any


class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class ToolSource(metaclass=SingletonMeta):
    def __init__(self, source_name:str):
        super().__init__()
        self.SOURCE_NAME: str = source_name

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        return {}

