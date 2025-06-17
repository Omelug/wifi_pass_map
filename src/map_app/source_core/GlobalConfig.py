import configparser
import glob
import os
import shutil
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

        default_config['Create backup'] = {
            'plugins': 'true',
            'config': 'true',
            'data': 'true',
            'backup_path': 'backup',
        }
        default_config['Load backup'] = {
            'override': 'true',
            'load_src_path': 'src',
        }
        super().__init__(type(self).__qualname__.lower(), default_config)

    def __create_backup(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        backup_cfg = config['Create backup']
        print(backup_cfg['data'])

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        def resolve_path(path):
            return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)

        backup_path = resolve_path(backup_cfg.get('backup_path'))
        os.makedirs(backup_path, exist_ok=True)

        if backup_cfg.getboolean('plugins', fallback=True):
            plugins_dst = os.path.join(backup_path, 'plugins')

            # Copy all ../sources/*.py to backup/plugins
            sources_dir = os.path.join(BASE_DIR, 'src', 'map_app', 'sources')
            py_files = glob.glob(os.path.join(sources_dir, '*.py'))
            os.makedirs(plugins_dst, exist_ok=True)
            for py_file in py_files:
                shutil.copy2(py_file, plugins_dst)

        if backup_cfg.getboolean('config', fallback=True):
            # Backup config folder if it exists
            config_folder_src = os.path.join(BASE_DIR, 'src', 'map_app', 'sources', 'config')
            config_folder_dst = os.path.join(backup_path, 'config')
            if os.path.isdir(config_folder_src):
                shutil.copytree(config_folder_src, config_folder_dst, dirs_exist_ok=True)

        if backup_cfg.getboolean('data', fallback=True):
            data_src = resolve_path('data')
            data_dst = os.path.join(backup_path, 'data')
            if os.path.exists(data_src):
                shutil.copytree(data_src, data_dst, dirs_exist_ok=True)

    def __load_backup(self):
        pass

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        config = configparser.ConfigParser()
        config.read(self.config_path())

        global_param = [
            ("ordered_sources", str, None, config['view_settings']['ordered_sources'], "Ordered listof sources"),
            ("start_map_point", str, None, config['start_view']['start_map_point'], "start map point zoom"),
            ("start_zoom", str, None, config['start_view']['start_zoom'], "start map zoom"),
        ]

        create_backup_param = [
            ("Backup plugins?", str, None, config['Create backup']['plugins'], "(true/false/only_custom)"),
            ("Backup config?", str, None, config['Create backup']['config'], "Ordered listof sources (true/false)"),
            ("data", str, None, config['Create backup']['data'], "(true/false)"),
            ("backup_path", str, None, config['Create backup']['backup_path'], "(true/false/run_select)"),
        ]

        load_backup_param = [
            ("override", str, None, config['Load backup']['override'], "(true/false)"),
            ("load_src_path", str, None, config['Load backup']['load_src_path'], "(true/false/run_select)"),
        ]

        return {
            "Global Settings": {"params": global_param},
            "Create backup": {"params": create_backup_param, "run_fun": self.__create_backup},
            "Load backup": {"params": load_backup_param, "run_fun": self.__load_backup}
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