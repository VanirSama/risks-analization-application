from .form import RiskAnalysisMainForm
from .actionHandler import ActionHandler
from PySide6.QtWidgets import QTabWidget, QMessageBox, QWidget, QVBoxLayout, QToolBar, QStatusBar, QMainWindow, \
    QPushButton, QTableWidgetItem, QFileDialog
from PySide6.QtGui import QAction, Qt, QIcon
from PySide6.QtCore import QTimer
from src.backend.riskMap import RiskMap
from .rusMsgBox import RusMsgBox
from .resources import *
from ..backend.convertion import RiskMapToDocxConverter


class RiskAnalysisMainWindow(QMainWindow):
    def __init__(self, createDefaultMap:bool=True, fileToOpen:str=None):
        super().__init__()
        self.setMinimumSize(400, 300)
        self.setWindowTitle("АУРА 1.0 ОПР")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setStyleSheet("""
            QWidget {
                background-color: #DCD6F7;
            }
            QToolTip {
                background-color: #F4EEFF
                color: #424874;
                border: 1px solid #A6B1E1;
                border-radius: 5px;
                font-size: 10px;
                opacity: 230;
            }
        """)
        self.autosaveTimer = QTimer()
        self.autosaveTimer.setInterval(300000)
        self.autosaveTimer.timeout.connect(self.autoSaveMaps)
        self.autosaveTimer.start()
        self._riskMaps = []
        self._currentMapIndex = -1
        self._actionHandler = ActionHandler(self)
        self.recentFilesManager = None

        self._tabWidget = QTabWidget()
        self._tabWidget.tabBar().setExpanding(False)
        self._tabWidget.tabBar().setUsesScrollButtons(True)
        self._tabWidget.tabBar().setElideMode(Qt.TextElideMode.ElideRight)
        self._tabWidget.setTabsClosable(True)
        self._tabWidget.setMovable(True)
        self._tabWidget.setDocumentMode(True)
        self._tabWidget.setStyleSheet("""
                    QTabWidget::pane {
                        border: none;
                        background: transparent;
                    }
                    QTabBar {
                        background: transparent;
                        border: none;
                    }
                    QTabBar::tab {
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
                    }
                    QTabBar::tab:selected {
                        background: #F4EEFF;
                    }
                    QTabBar::tab:!selected {
                        margin-top: 4px;
                    }
                    QTabBar::tab:hover {
                        background: #FFF;
                    }
                    QTabBar QToolButton {
                        background: #F4EEFF;
                        color: #424874;
                        border-radius: 5px;
                        padding: 2px;
                    }
                    QTabBar QToolButton:hover {
                        background: #FFFFFF;
                    }
                    QTabBar QToolButton:disabled {
                        background: #E9E4FF;
                    }
                """)
        self.setCentralWidget(self._tabWidget)

        self._toolBar = QToolBar()
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
                """)

        self.addToolBar(self._toolBar)
        menuActions = [("Создать", self._actionHandler.onNew, "Ctrl+N", "Создать пустую карту"),
                       ("Создать из шаблона", self._actionHandler.onNewFromTemplate, "Ctrl+Shift+N", "Создать карту из шаблона"),
                       ("Сохранить", self._actionHandler.onSave, "Ctrl+S", "Сохранить карту"),
                       ("Сохранить как", self._actionHandler.onSaveAs, "Ctrl+Shift+S", "Сохранить карту в выбранном формате"),
                       ("Открыть", self._actionHandler.onOpen, "Ctrl+O", "Открыть имеющуюся карту из выбранной папки"),
                       ("Помощь", self._actionHandler.onHelp, "Ctrl+H", "Получить подсказки по использованию приолжения")]

        for event, handler, shortcut, tooltip in menuActions:
            action = QAction(event, self)
            action.setShortcut(shortcut)
            action.setToolTip(f"{tooltip}: {shortcut}")
            action.triggered.connect(handler)
            self._toolBar.addAction(action)

        self.setStatusBar(QStatusBar(self))

        self._tabWidget.tabCloseRequested.connect(self.closeRiskMap)
        self._tabWidget.currentChanged.connect(self.switchRiskMap)
        if fileToOpen:
            risk_map = RiskMap.loadFromRsk(path=fileToOpen)
            if risk_map:
                self._riskMaps.append(risk_map)
                tab = self.RiskMapTab(risk_map)
                self._tabWidget.addTab(tab, risk_map.getTabName())
                self._tabWidget.setCurrentIndex(len(self._riskMaps) - 1)
                self._currentMapIndex = len(self._riskMaps) - 1
                tab.updateFormFromRisk()
        elif createDefaultMap:
            self.createNewRiskMap(fromTemplate=False)

        self._updateMenuActions()

    def autoSaveMaps(self):
        for i, riskMap in enumerate(self._riskMaps):
            if i != self._currentMapIndex:
                riskMap.autoSave()

    class RiskMapTab(QWidget):
        def __init__(self, riskMap: RiskMap, parent=None):
            super().__init__(parent)
            self.riskMap = riskMap
            self.form = RiskAnalysisMainForm(riskMap=self.riskMap)

            layout = QVBoxLayout(self)
            layout.addWidget(self.form)
            layout.setContentsMargins(0, 0, 0, 0)

            self.form.button_calculate.clicked.connect(self.onCalcButtonClicked)
            self.form.button_convert_to.clicked.connect(self.onConvertButtonClicked)
            self.updateFormFromRisk()

        def onCalcButtonClicked(self):
            if self.riskMap:
                result = self.riskMap.calculate()
                if result == 1:
                    if self.form and self.form.methodsDataTableWidget:
                        self.updateFormFromRisk()
                        RusMsgBox.information(self, "Расчет завершен", "Расчет рисков выполнен успешно!")

                elif result == 0:
                    RusMsgBox.information(self, "Ошибка расчета", "Не все обязательные поля заполнены!")
                else:
                    RusMsgBox.information(self, "Ошибка расчета", "Нет данных для расчета!")

        def onConvertButtonClicked(self):
            if self.riskMap:
                result = self.riskMap.calculate(updateMethods=False)
                if result == 1:
                    savePath, _ = QFileDialog.getSaveFileName(self,
                                                              "Сохранить файл отчета",
                                                              "",
                                                              "Документы MS Word (*.docx)")
                    if not savePath:
                        return
                    try:
                        converter = RiskMapToDocxConverter(self.riskMap)
                        converter.convertToDocx(savePath)
                    except PermissionError:
                        RusMsgBox.information(self, "Ошибка сохранения", f"Файл {savePath} недоступен для перезаписи.\nЗакройте файл и повторите операцию.")
                elif result == 0:
                    RusMsgBox.information(self, "Ошибка конвертирования", "Не все обязательные поля заполнены!")
                else:
                    RusMsgBox.information(self, "Ошибка конвертирования", "Нет данных для расчета!")

        def updateFormFromRisk(self):
            if self.form and self.riskMap:
                self.form.setQLineBlockSignals(True)
                self.form.mapNo_text = self.riskMap.mapNo if self.riskMap.mapNo else ""
                self.form.profession_text = self.riskMap.profession if self.riskMap.profession else ""
                self.form.structure_division_text = self.riskMap.structDivision if self.riskMap.structDivision else ""
                self.form.work_description_text = self.riskMap.description if self.riskMap.description else ""
                self.form.used_materials_text = self.riskMap.toolsMaterials if self.riskMap.toolsMaterials else ""
                self.form.chairman_fullname_text = self.riskMap.chairman if self.riskMap.chairman else ""

                if self.riskMap.resultStr:
                    self.form.summary_risk_level_text = str(round(self.riskMap.profRisk, 2)) if self.riskMap.profRisk else ""
                    self.form.summary_risk_indicator_text = str(self.riskMap.kFactor) if self.riskMap.kFactor else ""
                    self.form.summary_risk_final_level_text = str(round(self.riskMap.result, 2)) if self.riskMap.result else ""
                    self.form.summary_risk_classification_text = self.riskMap.resultStr

                self.form.setQLineBlockSignals(False)

                self.form.riskDataTableWidget.setRowCount(0)
                for record in self.riskMap.table:
                    row = self.form.riskDataTableWidget.rowCount()
                    self.form.riskDataTableWidget.insertRow(row)

                    removeButton = QPushButton('-')
                    removeButton.setObjectName('ManageRowButtonDelete')
                    removeButton.clicked.connect(self.form.riskDataTableWidget.on_remove_row_clicked)
                    self.form.riskDataTableWidget.setCellWidget(row, 0, removeButton)

                    item1 = QTableWidgetItem(str(row + 1))
                    item1.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                    self.form.riskDataTableWidget.setItem(row, 1, item1)

                    item2 = QTableWidgetItem(f"{record.n}. {record.danger}")
                    item2.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                    self.form.riskDataTableWidget.setItem(row, 2, item2)

                    if record.event:
                        item3 = QTableWidgetItem(record.event)
                        item3.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                        self.form.riskDataTableWidget.setItem(row, 3, item3)

                    if record.damage:
                        item4 = QTableWidgetItem(record.damage)
                        item4.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                        self.form.riskDataTableWidget.setItem(row, 4, item4)

                    if record.susceptibility:
                        item5 = QTableWidgetItem(record.susceptibility)
                        item5.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                        self.form.riskDataTableWidget.setItem(row, 5, item5)

                    if record.probability:
                        item6 = QTableWidgetItem(record.probability)
                        item6.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                        self.form.riskDataTableWidget.setItem(row, 6, item6)

                    if record.rating:
                        item7 = QTableWidgetItem(record.rating)
                        item7.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                        self.form.riskDataTableWidget.setItem(row, 7, item7)

                self.form.riskDataTableWidget._initialize_default_row()

                if self.riskMap._methodModified:
                    self.form.methodsDataTableWidget.setRowCount(0)
                    for method in self.riskMap.methods:
                        row = self.form.methodsDataTableWidget.rowCount()
                        self.form.methodsDataTableWidget.insertRow(row)

                        remove_button = QPushButton('-')
                        remove_button.setObjectName('ManageRowButton')
                        remove_button.clicked.connect(self.form.methodsDataTableWidget._onRemoveMethodClicked)
                        self.form.methodsDataTableWidget.setCellWidget(row, 0, remove_button)

                        item = QTableWidgetItem(method)
                        item.setFlags(Qt.ItemFlag.NoItemFlags)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                        self.form.methodsDataTableWidget.setItem(row, 1, item)
                    self.form.methodsDataTableWidget._initialize_default_row()

                    self.form.riskDataTableWidget.updateHeight()
                    self.form.methodsDataTableWidget.updateHeight()
                    self.riskMap._methodModified = False
            else:
                return

    def setRecentFilesManager(self, manager):
        self.recentFilesManager = manager

    def createNewRiskMap(self, fromTemplate=False, templatePath=None):
        self.setUpdatesEnabled(False)
        riskMap: RiskMap = None
        if fromTemplate:
            if templatePath:
                riskMap = RiskMap.loadFromRsk(path=templatePath)
            if riskMap:
                riskMap._savePath = None
                riskMap._name = None
        else:
            riskMap = RiskMap()

        if riskMap:
            existingNames = {rm.name for rm in self._riskMaps}
            baseName = riskMap.name if riskMap.name else "Новая карта"
            counter = 1
            newName = baseName
            while newName in existingNames:
                riskMap.name = f"{baseName} ({counter})"
                counter += 1
            riskMap.name = newName

            self._riskMaps.append(riskMap)
            tab = self.RiskMapTab(riskMap)
            self._tabWidget.addTab(tab, riskMap.getTabName())
            self._tabWidget.setCurrentIndex(len(self._riskMaps) - 1)
            self._currentMapIndex = len(self._riskMaps) - 1
            self.setUpdatesEnabled(True)

    def closeRiskMap(self, index):
        if index < 0 or index >= len(self._riskMaps):
            return
        if self._riskMaps[index].isModified:
            reply = RusMsgBox.question(
                self,
                'Сохранение изменений',
                f'Сохранить изменения в карте "{self._riskMaps[index].name}" перед закрытием?')
            if reply == QMessageBox.StandardButton.Cancel:
                pass
            elif reply == QMessageBox.StandardButton.Yes:
                self._currentMapIndex = index
                self._actionHandler.onSave()
        self._tabWidget.removeTab(index)
        del self._riskMaps[index]

        if len(self._riskMaps) == 0:
            from src.ui.mainMenu import MainMenuWindow
            RiskMap._new_map_counter = 1
            self.mainMenu = MainMenuWindow()
            self.mainMenu.showMaximized()
            self.close()
        else:
            self._currentMapIndex = min(index, len(self._riskMaps) - 1)
            self._tabWidget.setCurrentIndex(self._currentMapIndex)

    def switchRiskMap(self, index):
        if index < 0 or index >= len(self._riskMaps):
            return
        self._currentMapIndex = index
        currentTab = self._tabWidget.widget(index)
        if currentTab and isinstance(currentTab, self.RiskMapTab):
            currentTab.updateFormFromRisk()
        self._updateMenuActions()

    def currentRiskMap(self):
        if 0 <= self._currentMapIndex < len(self._riskMaps):
            return self._riskMaps[self._currentMapIndex]
        return None

    def _updateMenuActions(self):
        has_map = self.currentRiskMap() is not None
        for action in self.findChildren(QAction):
            if action.text() in ["Сохранить", "Сохранить как"]:
                action.setEnabled(has_map)

    @property
    def riskMaps(self) -> list[RiskMap, ...]:
        return self._riskMaps

    @property
    def tabWidget(self) -> QTabWidget:
        return self._tabWidget
