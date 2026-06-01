from src.ui.components.recent_files_grid import RecentFilesGrid
from src.ui.styles.fonts import Fonts
from src.ui.styles.qss_styles import Styles

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea


class MainMenuPage(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel('Добро пожаловать в "АУРА"')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: #4a4a7d;
                font-size: 36px;
                font-weight: light;
                font-family: "{Fonts.STROGO}";
                margin: 20px;
            }}""")

        self.recent_files_grid = RecentFilesGrid()

        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(Styles.SCROLL_AREA)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.recent_files_grid)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        label = QLabel("Недавние файлы")
        label.setStyleSheet("""
            QLabel {
                color: #4a4a7d;
                font-size: 20px;
                font-weight: bold;
                margin-top: 15px;
                margin-left: 50px;
            }
        """)

        layout.addWidget(title)
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(scroll_area)