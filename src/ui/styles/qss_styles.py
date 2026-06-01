from src.utils.resources import ResourceLoader
from src.utils.utils import normalize_path

from PySide6.QtCore import QDir


class Styles:
    QDir.addSearchPath("icons", normalize_path(ResourceLoader.ICONS))
    _CLOSE_ICON = "url(icons:close_button.svg)"
    
    SCROLL_AREA = """
    QScrollBar:horizontal {
        border: none;
        border-radius: 4px;
        background: transparent;
        height: 10px;
        margin: 0px 20px 0 20px;
    }
    QScrollBar::handle:horizontal {
        background: #A6B1E1;
        min-width: 20px;
        border-radius: 4px;
    }
    QScrollBar::add-line:horizontal {
        border: none;
        background: #DCD6F7;
        width: 15px;
        height: 10px;
        subcontrol-position: right;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:horizontal {
        border: none;
        background: #DCD6F7;
        width: 15px;
        height: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:horizontal {
        border: none;
        background: #DCD6F7;
        width: 15px;
        height: 10px;
        subcontrol-position: left;
        subcontrol-origin: margin;
    }
    QScrollBar:vertical {
        border: none;
        border-radius: 4px;
        background: #DCD6F7;
        width: 10px;
        margin: 20px 0 20px 0;
    }
    QScrollBar::handle:vertical {
        background: #A6B1E1;
        min-height: 15px;
        border-radius: 4px;
    }
    QScrollBar::add-line:vertical {
        border: none;
        background: #DCD6F7;
        height: 15px;
        width: 10px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        border: none;
        background: #DCD6F7;
        height: 15px;
        width: 10px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical,
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        background: transparent;
    }
"""

    MENU_BAR = """
    QMenuBar {
        background: qlineargradient(
            x1: 0, y1: 0, 
            x2: 1, y2: 1,
            stop: 0 #241d50, 
            stop: 1 #383e92
        );
        border: none;
        spacing: 5px;
    }
    QMenuBar::item {
        background-color: transparent;
        color: #ffffff;
        padding: 5px 10px;
        border: none;
        font-size: 14px;
    }
    QMenuBar::item:selected {
        background-color: #1b1542;
    }
    QMenuBar::item:pressed {
        background-color: #1b1542;
    }
    QMenuBar::item:disabled {
        color: #a0a0a0;
        background-color: transparent;
    }
    QMenu {
        background-color: #E9E4FF;
        color: #4a4a7d;
        font-size: 12px;
        border: 1px solid #4a4a7d;
        border-radius: 5px;
        padding: 2px;
    }
    QMenu::item {
        background-color: transparent;
        color: #4a4a7d;
        padding: 5px 30px 5px 20px;
        border: none;
        border-radius: 3px;
        font-size: 12px;
    }
    QMenu::item:selected {
        background-color: #A6B1E1;
    }
    QMenu::item:disabled {
        color: #a0a0a0;
        background-color: transparent;
    }
    QMenu::separator {
        height: 1px;
        background-color: #4a4599;
        margin: 5px 5px;
    }
"""

    TABLE = """
    QTableWidget {
        gridline-color: #4a4a7d;
        background-color: #F4EEFF;
        border: 1px solid #4a4a7d;
    }
    QTableWidget::item {
        height: 40;
        color: #424874;
        font-size: 14px;
        font-weight: bold;
        text-align: center;
        border-left: 1px solid #4a4a7d;
    }
    QHeaderView::section {
        height: 30;
        background-color: #F4EEFF;
        color: #4a4a7d;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        border: 1px solid #4a4a7d;
    }
    QLineEdit {
        background-color: #F4EEFF;
        color: #424874;
        font-size: 14px;
    }
    QPushButton#ManageRowButtonAdd {
        background-color: #F4EEFF;
        color: #4a4a7d;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        border: 2px solid #4a4a7d;
        border-radius: 5px;
        margin: 3px 3px 3px 3px;
    }
    QPushButton#ManageRowButtonDelete {
        background-color: #F4EEFF;
        color: #A6B1E1;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        border: 2px solid #A6B1E1;
        border-radius: 5px;
        margin: 3px 3px 3px 3px;
    }
    QPushButton#ManageRowButtonAdd:hover {
        background-color: #a6b1e1;
    }
    QPushButton#ManageRowButtonDelete:hover {
        background-color: #a6b1e1;
        color: #4a4a7d;
        border: 2px solid #4a4a7d;
    }
"""

    METHODS_TABLE = """
    QTableWidget {
        gridline-color: #4a4a7d;
        background-color: #F4EEFF;
        border: 1px solid #4a4a7d
    }
    QTableWidget::item {
        height: 40;
        color: #424874;
        font-size: 14px;
        text-align: center;
        border-left: 1px solid #4a4a7d
    }
    QHeaderView::section {
        height: 30;
        background-color: #F4EEFF;
        color: #4a4a7d;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        border: 1px solid #4a4a7d;
    }
    QPushButton#ManageRowButton {
        background-color: #F4EEFF;
        color: #4a4a7d;
        font-weight: bold;
        font-size: 14px;
        text-align: center;
        border: 2px solid #4a4a7d;
        border-radius: 5px;
        margin: 3px 3px 3px 3px;
    }
    QPushButton#ManageRowButton:hover {
        background-color: #a6b1e1;
    }
"""

    MESSAGE_BOX = """
    QMessageBox {
        background-color: #F4EEFF;
    }
    QMessageBox QLabel {
        background-color: #F4EEFF;
        color: #4a4a7d;
        font-size: 14px;
        text-align: center;
    }
    QMessageBox QPushButton {
        background-color: #DCD6F7;
        color: #4a4a7d;
        border: none;
        padding: 5px 10px;
        border-radius: 5px;
        min-width: 80px;
    }
    QMessageBox QPushButton:hover {
        background-color: #A6B1E1;
    }
    QMessageBox QPushButton:pressed {
        background-color: #424874;
        color: #F4EEFF;
    }"""


    TAB_WIDGET = f"""
    QTabWidget::pane {{
        border: none;
        background: transparent;
    }}
    QTabBar {{
        background: transparent;
        border: none;
    }}
    QTabBar::tab {{
        background: #E9E4FF;
        color: #424874;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 10px;
        border: none;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        min-width: 20px;
        max-width: 300px;
    }}
    QTabBar::tab:selected {{
        background: #F4EEFF;
    }}
    QTabBar::tab:!selected {{
        margin-top: 4px;
    }}
    QTabBar::tab:!selected QTabBar::close-button {{
        image: none;
    }}
    
    QTabBar::tab:hover {{
        background: qlineargradient(
            x1: 0, y1: 0, 
            x2: 0, y2: 1,
            stop: 0 #FFFFFF, 
            stop: 1 #F4EEFF
        );
    }}
    QTabBar::close-button {{
        image: {_CLOSE_ICON};
        background: transparent;
        color: #F4EEFF;
        border-radius: 5px;
        subcontrol-position: right;
        margin-right: 4px;
        width: 64px;
        height: 64px;
    }}
    
    QTabBar::close-button:hover {{
        color: #1b1542;
    }}
    QTabBar::close-button:pressed {{
        color: #1b1542;
    }}
    """
    COMBO_BOX = """
    QComboBox {
        background-color: #F4EEFF;
        color: #424874;
        font-size: 14px;
        text-align: left;
        border: 1px solid #4a4a7d;
    }
    QComboBox QAbstractItemView {
        background-color: #F4EEFF;
        color: #424874;
        selection-background-color:#a6b1e1;
        selection-color: #4a4a7d;
    }
    """
