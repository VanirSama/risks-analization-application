from src.core.database.manager import DatabaseManager
from src.ui.styles.qss_styles import Styles

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QStyledItemDelegate, QTableWidget, QComboBox, QCompleter, QListView, QApplication


class MultiLineItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option, index):
        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            doc = option.widget.fontMetrics()
            width = option.rect.width() if option.rect.width() > 0 else 300
            rect = doc.boundingRect(0, 0, width, 0,
                                   Qt.TextFlag.TextWordWrap, text)
            return QSize(width, rect.height() + 10)  # Add padding
        return super().sizeHint(option, index)


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, app: QApplication, parent: QTableWidget = None):
        super().__init__(parent)
        self._app = app
        self.parent_table = parent

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setEditable(True)
        editor.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        editor.completer().setCompletionMode(QCompleter.PopupCompletion)
        editor.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        view = QListView()
        view.setWordWrap(True)
        view.setTextElideMode(Qt.TextElideMode.ElideNone)
        view.setItemDelegate(MultiLineItemDelegate(view))
        editor.setView(view)

        editor.setStyleSheet(Styles.COMBO_BOX)

        if index.column() == 2:
            editor.addItems(self._app.database_manager.dangers)

        elif index.column() == 3:
            danger_item = self.parent_table.item(index.row(), 2)
            if danger_item and danger_item.text(): editor.addItems(self._app.database_manager.get_events(danger_item.text()))

        elif index.column() == 4:
            editor.addItems(DatabaseManager.DAMAGE.keys())
        elif index.column() == 5:
            editor.addItems(DatabaseManager.SUSCEPTIBILITY.keys())
        elif index.column() == 6:
            editor.addItems(DatabaseManager.PROBABILITY.keys())

        editor.setCurrentIndex(-1)
        editor.lineEdit().clear()

        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        if value and str(value).strip():
            idx = editor.findText(str(value))
            if idx >= 0:
                editor.setCurrentIndex(idx)
            else:
                editor.setCurrentText(str(value))
        else:
            editor.setCurrentIndex(-1)
            editor.lineEdit().clear()

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)