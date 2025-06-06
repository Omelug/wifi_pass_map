from abc import abstractmethod
from typing import Dict, Any, Optional

from src.map_app.source_core.ToolSource import ToolSource


class MapSource(ToolSource):
    def __init__(self, source_name:str, config:Dict[str, Any]=None):
        super().__init__(source_name, config)

    @abstractmethod
    def get_map_data(self, filters: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
        pass
