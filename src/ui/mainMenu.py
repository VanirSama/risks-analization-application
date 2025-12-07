from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout, QStatusBar, \
    QFileDialog, QFrame, QSizePolicy, QScrollArea
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import Qt, QSize
from .resources import RECENT_FILES_JSON, APP_ICON, DOCUMENT_ICON_LOGO
from .rusMsgBox import RusMsgBox
from ..backend import riskMap
from .actionHandler import ActionHandler
from pathlib import Path
import json


class RecentFilesManager:
    def __init__(self, historyFile=RECENT_FILES_JSON, maxFiles: int = 40):
        self.historyFile = historyFile
        self.maxFiles = maxFiles
        self.recentFiles = self.loadHistory()

    def loadHistory(self):
        try:
            if Path(self.historyFile).exists():
                with open(self.historyFile, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def saveHistory(self):
        with open(self.historyFile, "w", encoding="utf-8") as f:
            json.dump(self.recentFiles, f, ensure_ascii=False, indent=4)

    def addFile(self, filePath):
        if filePath in self.recentFiles:
            self.recentFiles.remove(filePath)
        self.recentFiles.insert(0, filePath)
        if len(self.recentFiles) > self.maxFiles:
            self.recentFiles = self.recentFiles[:self.maxFiles]
        self.saveHistory()

    def getRecentFiles(self):
        return self.recentFiles.copy()


class RecentFilesGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout(self)
        self.layout.setSpacing(32)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.current_row = 0
        self.current_col = 0
        self.max_columns = 11
        self.parent = parent

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def addFile(self, filePath, icon):
        if self.current_col >= self.max_columns:
            self.current_row += 1
            self.current_col = 0

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #DCD6F7;
                border-radius: 10px;
            }
            QFrame:hover {
                background: #E9E4FF;
            }
        """)
        card.setFixedSize(140, 175)

        card.setObjectName("recentFileCard")
        card.setAttribute(Qt.WA_Hover, True)

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        pixmap = icon.pixmap(QSize(128, 128))
        icon_label.setPixmap(pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent;")

        file_name = QLabel(Path(filePath).name)
        file_name.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #4a4a7d;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        file_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        file_name.setWordWrap(True)
        file_name.setMaximumWidth(100)
        file_name.setStyleSheet("""
            QLabel {
                background: transparent;
                color: #4a4a7d;
                font-size: 12px;
            }
        """)

        card_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(file_name, alignment=Qt.AlignmentFlag.AlignCenter)

        card.mousePressEvent = lambda event, path=filePath: self._onCardClicked(path)

        self.layout.addWidget(card, self.current_row, self.current_col, alignment=Qt.AlignmentFlag.AlignLeft)
        self.current_col += 1

    def _onCardClicked(self, filePath):
        if hasattr(self.parent, '_onRecentFileClicked'):
            self.parent._onRecentFileClicked(filePath)


class MainMenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 300)
        self._actionHandler = ActionHandler(self)
        self.recentFilesManager = RecentFilesManager()
        self.setWindowTitle("АУРА 1.0 ОПР")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setStyleSheet("""
            QWidget {
                background-color: #DCD6F7;
            }
            QLabel {
                color: #4a4a7d;
                font-size: 12px;
            }
            QScrollArea {
                border: none;
            }
            #recentFileCard > * {
                background: transparent;
            }
        """)
        self._setupUI()
        self._setupToolbar()
        self._loadRecentFiles()

    def _setupUI(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 10, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Добро пожаловать в АУРА")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""color: #4a4a7d; font-size: 30px; font-weight: light; margin: 10px;""")

        self.recentFilesGrid = RecentFilesGrid(self)
        self.recentFilesGrid.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                border-radius: 10px;
                margin: 0px 50px 10px 50px;
            }
        """)

        scroll_area = QScrollArea()
        scroll_area.setStyleSheet("""
            QScrollBar:horizontal {
                border: none;
                border-radius: 5px;
                background: transparent;
                height: 14px;
                margin: 0px 20px 0 20px;
            }
            QScrollBar::handle:horizontal {
                background: #A6B1E1;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal {
                border: none;
                background: #DCD6F7;
                width: 20px;
                height: 14px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:horizontal {
                border: none;
                background: #DCD6F7;
                width: 20px;
                height: 14px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:horizontal {
                border: none;
                background: #DCD6F7;
                width: 20px;
                height: 14px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar:vertical {
                border: none;
                border-radius: 5px;
                background: #DCD6F7;
                width: 14px;
                margin: 20px 0 20px 0;
            }
            QScrollBar::handle:vertical {
                background: #A6B1E1;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: #DCD6F7;
                height: 20px;
                width: 14px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: #DCD6F7;
                height: 20px;
                width: 14px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: transparent;
            }""")
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.recentFilesGrid)
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

        self.setCentralWidget(central_widget)

    def _setupToolbar(self):
        self._toolBar = self.addToolBar("Main Toolbar")
        self._toolBar.setMovable(False)
        self._toolBar.setStyleSheet("""
                            QToolBar {
                                background: qlineargradient(
                                    x1: 0, y1: 0, 
                                    x2: 1, y2: 1,
                                    stop: 0 #241d50, 
                                    stop: 1 #383e92
                                );
                                border: none;
                                spacing: 5px;
                            }
                            QToolButton {
                                background-color: transparent;
                                color: #ffffff;
                                padding: 5px 10px;
                                border: none;
                                border-radius: 0px;
                                font-size: 14px;
                            }
                            QToolButton:pressed {
                                background-color: #1b1542;
                            }
                            QToolButton:hover {
                                background-color: #1b1542;
                            }
                            QToolButton:disabled {
                                color: #a0a0a0;
                                background-color: transparent;
                            }
                        """)

        actions = [
            ("Создать", self._onNewClicked, "Ctrl+N", "Создать пустую карту"),
            ("Создать из шаблона", self._onNewFromTemplateClicked, "Ctrl+Shift+N", "Создать карту из шаблона"),
            ("Сохранить", self._onSave, "Ctrl+S", "Сохранить карту"),
            ("Сохранить как", self._onSaveAs, "Ctrl+Shift+S", "Сохранить карту в выбранном формате"),
            ("Открыть", self._onOpen, "Ctrl+O", "Открыть имеющуюся карту из выбранной папки"),
            ("Помощь", self._actionHandler.onHelp, "Ctrl+H", "Получить подсказки по использованию приолжения")
        ]

        for event, handler, shortcut, tooltip in actions:
            action = QAction(event, self)
            if event != "Сохранить" and event != "Сохранить как":
                pass
            else:
                action.setEnabled(False)
            action.setShortcut(shortcut)
            action.setToolTip(f"{tooltip}: {shortcut}")
            action.triggered.connect(handler)
            self._toolBar.addAction(action)
        self.setStatusBar(QStatusBar(self))

    def _loadRecentFiles(self):
        for i in reversed(range(self.recentFilesGrid.layout.count())):
            widget = self.recentFilesGrid.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.recentFilesGrid.current_row = 0
        self.recentFilesGrid.current_col = 0

        recentFiles = self.recentFilesManager.getRecentFiles()
        for filePath in recentFiles:
            icon = QIcon(DOCUMENT_ICON_LOGO) if filePath.endswith(".rsk") else QIcon("text-x-generic")
            self.recentFilesGrid.addFile(filePath, icon)

    def _onRecentFileClicked(self, filePath):
        if Path(filePath).exists():
            self._onOpenRecent(filePath)
        else:
            self.recentFilesManager.recentFiles.remove(filePath)
            self.recentFilesManager.saveHistory()

            self._loadRecentFiles()

            RusMsgBox.information(
                self,
                "Файл не найден",
                f"Файл {Path(filePath)} не существует или был удален")

    def _onNewClicked(self):
        from src.ui.riskTabs import RiskAnalysisMainWindow
        self.risk_window = RiskAnalysisMainWindow(createDefaultMap=True)
        self.risk_window.setRecentFilesManager(self.recentFilesManager)
        self.risk_window.showMaximized()
        self.hide()
        self._loadRecentFiles()

    def _onNewFromTemplateClicked(self):
        from src.ui.riskTabs import RiskAnalysisMainWindow
        self.risk_window = RiskAnalysisMainWindow(createDefaultMap=False)
        self.risk_window.setRecentFilesManager(self.recentFilesManager)
        self.risk_window.showMaximized()
        templatePath, _ = QFileDialog.getOpenFileName(self.risk_window,
                                                      "Выберите шаблон карты рисков",
                                                      "templates",
                                                      "Файлы шаблонов (*.rsk)")
        if templatePath:
            self.risk_window.createNewRiskMap(fromTemplate=True, templatePath=templatePath)
        self.close()
        self._loadRecentFiles()

    def _onSave(self):
        pass

    def _onSaveAs(self):
        pass

    def _onOpenRecent(self, filePath):
        from src.ui.riskTabs import RiskAnalysisMainWindow
        self.riskWindow = RiskAnalysisMainWindow(createDefaultMap=False)
        self.riskWindow.setRecentFilesManager(self.recentFilesManager)
        self.riskWindow.showMaximized()
        self.hide()
        risk_map = riskMap.RiskMap.loadFromRsk(path=filePath)
        if risk_map:
            existing_names = {rm.name for rm in self.riskWindow.riskMaps}
            base_name = risk_map.name
            counter = 1
            while risk_map.name in existing_names:
                risk_map.name = f"{base_name} ({counter})"
                counter += 1
            newTab = self.riskWindow.RiskMapTab(risk_map)
            self.riskWindow.riskMaps.append(risk_map)
            self.riskWindow.tabWidget.addTab(newTab, risk_map.getTabName())
            self.riskWindow.tabWidget.setCurrentIndex(len(self.riskWindow.riskMaps) - 1)
            self.riskWindow._currentMapIndex = len(self.riskWindow.riskMaps) - 1
            newTab.updateFormFromRisk()
            self._loadRecentFiles()

    def _onOpen(self):
        filePath, _ = QFileDialog.getOpenFileName(self,
                                                  "Открыть файл карты рисков",
                                                  "",
                                                  "Файлы карт рисков (*.rsk)")
        if not filePath:
            return
        from src.ui.riskTabs import RiskAnalysisMainWindow
        self.riskWindow = RiskAnalysisMainWindow(createDefaultMap=False)
        self.riskWindow.setRecentFilesManager(self.recentFilesManager)
        self.riskWindow.showMaximized()
        self.hide()
        risk_map = riskMap.RiskMap.loadFromRsk(path=filePath)
        if risk_map:
            self.recentFilesManager.addFile(filePath)
            existing_names = {rm.name for rm in self.riskWindow.riskMaps}
            base_name = risk_map.name
            counter = 1
            while risk_map.name in existing_names:
                risk_map.name = f"{base_name} ({counter})"
                counter += 1
            newTab = self.riskWindow.RiskMapTab(risk_map)
            self.riskWindow.riskMaps.append(risk_map)
            self.riskWindow.tabWidget.addTab(newTab, risk_map.getTabName())
            self.riskWindow.tabWidget.setCurrentIndex(len(self.riskWindow.riskMaps) - 1)
            self.riskWindow._currentMapIndex = len(self.riskWindow.riskMaps) - 1
            newTab.updateFormFromRisk()
            self._loadRecentFiles()
