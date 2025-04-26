from typing import Dict, Any

class SingletonMeta(type):
    """A metaclass for creating Singleton classes."""
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Source(metaclass=SingletonMeta):
    def __init__(self, source_name):
        super().__init__()
        self.SOURCE_NAME = source_name
    """
    "run_fun": function_to_run
    "params": List[tuple[str, type,None,Any]]
    """
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        pass

    def get_map_data(self, filters=None):
        pass