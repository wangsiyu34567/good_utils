import logging
import os
import threading
from configparser import ConfigParser, NoOptionError
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

lock = threading.Lock()


class ConfigFileModifyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.relpath(event.src_path) == 'app.config':
            Config.get_instance().load_config()


class Config(object):
    __instance = None

    def __init__(self, config_file_path=None):
        logging.debug('配置初始化')
        self.config = ConfigParser()
        self.config_file_path = config_file_path or os.path.join(os.path.dirname(__file__), '../app.config')
        self.load_config()
        self._init_config_file_observer()

    def _init_config_file_observer(self):
        logging.debug('配置文件监控')
        event_handler = ConfigFileModifyHandler()
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(self.config_file_path), recursive=False)
        observer.setDaemon(True)
        observer.start()

    @staticmethod
    def get_instance():
        if Config.__instance:
            return Config.__instance
        try:
            lock.acquire()
            if not Config.__instance:
                Config.__instance = Config()
        finally:
            lock.release()
        return Config.__instance

    def load_config(self):
        logging.debug('加载配置')
        self.config.read(self.config_file_path, 'utf-8')

    def get(self, key, default=None):
        """
        获取配置
        :param str key: 格式 [section].[key] 如：app.name
        :param Any default: 默认值
        :return:
        """
        map_key = key.split('.')
        if len(map_key) < 2:
            return default
        section = map_key[0]
        if not self.config.has_section(section):
            return default
        option = '.'.join(map_key[1:])
        try:
            return self.config.get(section, option)
        except NoOptionError:
            return default


def get(key, default=None):
    """
    获取配置
    :param str key: 格式 [section].[key] 如：app.name
    :param Any default: 默认值
    :return:
    """
    return Config.get_instance().get(key, default)