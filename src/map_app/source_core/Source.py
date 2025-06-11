from abc import abstractmethod
from typing import Dict, Any, Optional

from map_app.source_core.ToolSource import ToolSource


class MapSource(ToolSource):
    def __init__(self, source_name:str = None, config:Dict[str, Any]=None):
        if source_name is None:
            self.SOURCE_NAME = "mapsource"
            return
        super().__init__(source_name, config)

    @abstractmethod
    def get_map_data(self, filters: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        pass

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        return None