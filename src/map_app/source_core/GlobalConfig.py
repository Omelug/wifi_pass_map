import configparser
import glob
import os
import shutil
from typing import Dict, Any

from formator.param_validator import valid_relative_path
from map_app.source_core.ToolSource import ToolSource, SingletonMeta


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

        default_config['create_backup'] = {
            'plugins': 'true',
            'config': 'true',
            'data': 'true',
            'backup_folder_path': 'backup',
        }
        default_config['load_backup'] = {
            'override': 'true',
            'load_src_path': 'src',
        }
        super().__init__(type(self).__qualname__.lower(), default_config)

    def __create_backup(self):
        config = configparser.ConfigParser()
        config.read(self.config_path())
        backup_cfg = config['create_backup']
        print(backup_cfg['data'])

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        def resolve_path(path):
            return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)

        backup_path = resolve_path(backup_cfg.get('backup_folder_path'))
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

        config = configparser.ConfigParser()
        config.read(self.config_path())
        load_cfg = config['load_backup']

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        def resolve_path(path):
            return path if os.path.isabs(path) else os.path.join(BASE_DIR, path)

        override = load_cfg.getboolean('override', fallback=True)
        load_src_path = resolve_path(load_cfg.get('load_src_path', 'src'))
        backup_path = resolve_path(config['create_backup'].get('backup_path', 'backup'))

        # Restore config folder
        backup_config_folder = os.path.join(backup_path, 'config')
        target_config_folder = os.path.join(load_src_path, 'map_app', 'sources', 'config')
        if os.path.isdir(backup_config_folder):
            if override and os.path.isdir(target_config_folder):
                shutil.rmtree(target_config_folder)
            shutil.copytree(backup_config_folder, target_config_folder, dirs_exist_ok=True)

        # Restore plugins
        backup_plugins_folder = os.path.join(backup_path, 'plugins')
        target_plugins_folder = os.path.join(load_src_path, 'map_app', 'sources')
        if os.path.isdir(backup_plugins_folder):
            if override:
                for f in glob.glob(os.path.join(target_plugins_folder, '*.py')):
                    os.remove(f)
            for py_file in glob.glob(os.path.join(backup_plugins_folder, '*.py')):
                shutil.copy2(py_file, target_plugins_folder)

        # Restore data
        backup_data_folder = os.path.join(backup_path, 'data')
        target_data_folder = resolve_path('data')
        if os.path.isdir(backup_data_folder):
            if override and os.path.isdir(target_data_folder):
                shutil.rmtree(target_data_folder)
            shutil.copytree(backup_data_folder, target_data_folder, dirs_exist_ok=True)

        from map_app.source_core.manager import _load_source_objects  # Move import here
        SingletonMeta.clear_instances()
        #_ = _load_source_objects(ToolSource)

    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        from map_app.source_core.ToolSource import ToolGenerator
        gen = ToolGenerator(self)

        gen.addParam("view_settings", "ordered_sources", description="Ordered listof sources")
        gen.addParam("start_view", "start_map_point", description="start map point zoom")
        gen.addParam("start_view", "start_zoom", description="start map zoom")

        # Create backup
        gen.addParam("create_backup", "plugins", description="(true/false/only_custom)")
        gen.addParam("create_backup", "config", description="Ordered list of sources (true/false)")
        gen.addParam("create_backup", "data", description="(true/false)")
        gen.addParam("create_backup", "backup_folder_path", validation_function=valid_relative_path,
                     description="(true/false/run_select)")
        gen.add_run_fun("create_backup", self.__create_backup)

        # Load backup
        gen.addParam("load_backup", "override", description="(true/false)")
        gen.addParam("load_backup", "load_src_path", validation_function=os.path.exists,
                     description="(true/false/run_select)")
        gen.add_run_fun("load_backup", self.__load_backup)

        return gen.get_list()

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