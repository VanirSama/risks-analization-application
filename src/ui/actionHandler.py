from pathlib import Path
from .resources import TEMPLATES_FOLDER
from PySide6.QtWidgets import  QFileDialog
import sys, os
from ..backend import riskMap

class ActionHandler:
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

    def onHelp(self):
        pass

    def onNew(self):
        self.mainWindow.createNewRiskMap(False)

    def onNewFromTemplate(self):
        if getattr(sys, 'frozen', False):
            exeDir = Path(sys.executable).parent / "templates"
        else:
            exeDir = TEMPLATES_FOLDER
        templatesDir = str(exeDir)
        if not os.path.exists(templatesDir):
            os.mkdir(templatesDir)
        templatePath, _ = QFileDialog.getOpenFileName(self.mainWindow,
                                                      "Выберите шаблон карты рисков",
                                                      templatesDir,
                                                      "Файлы шаблонов (*.rsk)")
        if templatePath:
            self.mainWindow.createNewRiskMap(fromTemplate=True, templatePath=templatePath)
        else:
            return

    def onOpen(self):
        filePath, _ = QFileDialog.getOpenFileName(self.mainWindow,
                                                  "Открыть файл карты рисков",
                                                  "",
                                                  "Файлы карт рисков (*.rsk)")
        if not filePath:
            return
        risk_map = riskMap.RiskMap.loadFromRsk(path=filePath)
        if risk_map:
            risk_map.savePath = None
            risk_map._isModified = False
            if hasattr(self.mainWindow, "recentFilesManager"):
                self.mainWindow.recentFilesManager.addFile(filePath)
            existing_names = {rm.name for rm in self.mainWindow.riskMaps}
            base_name = risk_map.name
            counter = 1
            while risk_map.name in existing_names:
                risk_map.name = f"{base_name} ({counter})"
                counter += 1
            newTab = self.mainWindow.RiskMapTab(risk_map)
            self.mainWindow.riskMaps.append(risk_map)
            self.mainWindow.tabWidget.addTab(newTab, risk_map.getTabName())
            self.mainWindow.tabWidget.setCurrentIndex(len(self.mainWindow.riskMaps) - 1)
            self.mainWindow._currentMapIndex = len(self.mainWindow.riskMaps) - 1
            newTab.updateFormFromRisk()
            newTab._methodModified = False
            newTab.riskMap._isModified = False

    def onSave(self):
        risk_map = self.mainWindow.currentRiskMap()
        if not risk_map:
            return

        if not risk_map.savePath:
            self.onSaveAs()
            return

        risk_map.saveToRsk(risk_map.savePath)
        if hasattr(self.mainWindow, "recentFilesManager") and self.mainWindow.recentFilesManager:
            self.mainWindow.recentFilesManager.addFile(risk_map.savePath)
        self.mainWindow._tabWidget.setTabText(self.mainWindow._currentMapIndex, risk_map.getTabName())

    def onSaveAs(self):
        risk_map = self.mainWindow.currentRiskMap()
        if not risk_map:
            return

        savePath, _ = QFileDialog.getSaveFileName(self.mainWindow,
                                                  "Сохранить файл карты",
                                                  "",
                                                  "Файлы карт рисков (*.rsk)")
        if not savePath:
            return

        risk_map.name = Path(savePath).stem
        risk_map.savePath = savePath
        risk_map.saveToRsk(savePath)

        if hasattr(self.mainWindow, "recentFilesManager") and self.mainWindow.recentFilesManager:
            self.mainWindow.recentFilesManager.addFile(savePath)
        self.mainWindow._tabWidget.setTabText(self.mainWindow._currentMapIndex, risk_map.getTabName())
