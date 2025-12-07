from PySide6.QtWidgets import QSplashScreen
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from .resources import *

class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setFixedSize(320, 180)
        self.pixmap = QPixmap(SPLASH_SCREEN_LOGO)
        self.pixmap = self.pixmap.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.pixmap)
        self.setWindowFlag(Qt.FramelessWindowHint)
