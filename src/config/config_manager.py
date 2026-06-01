from src.utils.utils import SingletonMeta

from PySide6.QtWidgets import QApplication


class ConfigManager(metaclass=SingletonMeta):
    def __init__(self, app: QApplication):
        self._app = app