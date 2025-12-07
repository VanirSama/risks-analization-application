import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from src.ui.splash import SplashScreen
from src.ui.mainMenu import MainMenuWindow
from src.ui.riskTabs import RiskAnalysisMainWindow
from src.backend.riskMap import RiskMap
import sys
import os.path


if __name__ == '__main__':
    app = QApplication(sys.argv)

    if len(sys.argv) > 1 and sys.argv[1] == '--register':
        app_path = sys.executable
        sys.exit(0)

    file_to_open = None
    if len(sys.argv) > 1 and sys.argv[1].endswith('.rsk') and os.path.exists(sys.argv[1]):
        file_to_open = sys.argv[1]

    splash = SplashScreen()
    splash.show()


    def setup():
        main_menu = MainMenuWindow()
        if file_to_open:
            risk_window = RiskAnalysisMainWindow(createDefaultMap=False)
            risk_window.setRecentFilesManager(main_menu.recentFilesManager)
            risk_map = RiskMap.loadFromRsk(path=file_to_open)
            if risk_map:
                risk_window.riskMaps.append(risk_map)
                tab = risk_window.RiskMapTab(risk_map)
                risk_window.tabWidget.addTab(tab, risk_map.getTabName())
                risk_window.tabWidget.setCurrentIndex(len(risk_window.riskMaps) - 1)
                risk_window._currentMapIndex = len(risk_window.riskMaps) - 1
                tab.updateFormFromRisk()
            risk_window.showMaximized()
            splash.finish(risk_window)
        else:
            main_menu.showMaximized()
            splash.finish(main_menu)


    QTimer.singleShot(1500, setup)
    app.exec()
