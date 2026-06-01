from src.ui.styles.qss_styles import Styles
from src.utils.resources import ResourceLoader
from src.utils.utils import normalize_path

from dataclasses import dataclass
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar, QMenu
from typing import Callable, Optional


@dataclass
class MenuItem:
    text: Optional[str]
    callback: Optional[Callable] = None
    shortcut: Optional[str] = None
    icon: str = None
    tooltip: str = ""
    enabled: bool = True
    checkable: bool = False
    checked: bool = False


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setNativeMenuBar(False)
        self.setStyleSheet(Styles.MENU_BAR)
        self._export_action: Optional[QAction] = None

    def add_menu(self, title: str, items: list[MenuItem]) -> QMenu:
        menu = self.addMenu(title)
        for item in items:
            if item.text is None:
                menu.addSeparator()
                continue

            action = QAction(item.text, self)
            if item.shortcut: action.setShortcut(QKeySequence(item.shortcut))
            if item.tooltip: action.setToolTip(item.tooltip)
            action.setEnabled(item.enabled)
            action.setCheckable(item.checkable)
            if item.checkable: action.setChecked(item.checked)

            if item.callback: action.triggered.connect(item.callback)

            if item.text and item.text.startswith("Экспортировать"): self._export_action = action

            menu.addAction(action)
        return menu

    def set_export_for_risk_map(self):
        if self._export_action:
            self._export_action.setText("Экспортировать карту")
            self._export_action.setToolTip("Экспорт карты профессиональных рисков (Ctrl+P)")
            self._export_action.setEnabled(True)

    def set_export_for_risk_summary(self):
        if self._export_action:
            self._export_action.setText("Экспортировать сводную ведомость")
            self._export_action.setToolTip("Экспорт сводной ведомости (Ctrl+P)")
            self._export_action.setEnabled(True)

    def set_export_disabled(self):
        if self._export_action:
            self._export_action.setEnabled(False)

    def set_export_enabled(self, enabled: bool) -> None:
        if self._export_action:
            self._export_action.setEnabled(enabled)

    def set_action_enabled(self, text: str, enabled: bool) -> None:
        for menu in self.findChildren(QMenu):
            for action in menu.actions():
                if action.text() == text:
                    action.setEnabled(enabled)
                    return