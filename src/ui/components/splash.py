from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen


class SplashScreen(QSplashScreen):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self.setFixedSize(320, 180)
        self.pixmap = QPixmap(self._app.resource_loader.get("LOGO_WHITE", ""))
        self.pixmap = self.pixmap.scaled(320, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.pixmap)