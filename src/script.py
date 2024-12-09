from PySide6.QtWidgets import QApplication

from ui.window import RiskAnalysisMainWindow


if __name__ == '__main__':
    app = QApplication([])
    window = RiskAnalysisMainWindow()
    window.show()
    app.exec()

