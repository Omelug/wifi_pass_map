import configparser
from typing import Dict, Any

from map_app.source_core.ToolSource import ToolSource


class GlobalConfig(ToolSource):
    def __init__(self):
        default_config = configparser.ConfigParser()
        default_config['view_settings'] = {
            'ordered_sources': 'globalconfig,table_v0',
        }
        default_config['start_view'] = {
            'start_map_point': '49.8175,15.4730',
            'start_zoom': '7',
        }

        default_config['backup'] = {
            'plugins': 'true',
            'config': 'true',
            'data': 'true',
            'backup_path': 'backup',

            'override': 'true',
            'load_src_path': 'src',
        }
        super().__init__(type(self).__qualname__.lower(), default_config)

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        config = configparser.ConfigParser()
        config.read(self.config_path())

        global_param = [
            ("ordered_sources", str, None, config['view_settings']['ordered_sources'], "Ordered listof sources"),
            ("start_map_point", str, None, config['start_view']['start_map_point'], "start map point zoom"),
            ("start_zoom", str, None, config['start_view']['start_zoom'], "start map zoom"),
        ]

        create_backup_param = [
            ("Backup plugins?", str, None, config['backup']['plugins'], "(true/false/only_custom)"),
            ("Backup config?", str, None, config['backup']['config'], "Ordered listof sources (true/false)"),
            ("data", str, None, config['backup']['data'], "(true/false)"),
            ("backup_path", str, None, config['backup']['backup_path'], "(true/false/run_select)"),
        ]

        load_backup_param = [
            ("override", str, None, config['backup']['override'], "(true/false)"),
            ("load_src_path", str, None, config['backup']['load_src_path'], "(true/false/run_select)"),
        ]

        return {
            "Global Settings": {"params": global_param},
            "Create backup": {"params": create_backup_param},
            "Load backup": {"params": load_backup_param}
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

    def get_map_settings(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        point = config.get('start_view', 'start_map_point')
        zoom = config.get('start_view', 'start_zoom')
        lat, lng = map(float, point.split(','))
        return {'lat': lat, 'lng': lng, 'zoom': int(zoom)}