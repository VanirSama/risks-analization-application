from PySide6.QtWidgets import QMessageBox


class RusMsgBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
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
            }""")

    @staticmethod
    def critical(parent, title, message, *kwargs):
        msg = RusMsgBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.button(QMessageBox.StandardButton.Ok).setText("ОК")
        return msg.exec()

    @staticmethod
    def information(parent, title, message, *kwargs):
        msg = RusMsgBox(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.button(QMessageBox.StandardButton.Ok).setText("ОК")
        return msg.exec()

    @staticmethod
    def question(parent, title, message, *kwargs):
        msg = RusMsgBox(parent)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        msg.button(QMessageBox.StandardButton.Yes).setText("Да")
        msg.button(QMessageBox.StandardButton.Cancel).setText("Отмена")
        return msg.exec()
