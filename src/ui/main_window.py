from src.core.file_system import File, TFile
from src.models.risk_map import RiskMapFile
from src.models.risk_summary import RiskSummaryFile
from src.services.recent_files_manager import RecentFilesManager
from src.services.action_handler import ActionHandler
from src.ui.main_menu import MainMenuPage
from src.ui.risk_tabs import BaseTab, RiskMapTab, RiskSummaryTab
from src.ui.components.menu_bar import MenuBar, MenuItem
from src.ui.components.rus_msg_box import RusMsgBox
from src.ui.components.workspace_page import WorkspacePage
from src.utils.file_mapping import FileMapping
from src.utils.utils import normalize_path

from PySide6.QtWidgets import QMainWindow, QStackedWidget, QTabWidget, QStatusBar, QMessageBox, QFileDialog, QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from typing import Optional
from pathlib import Path


class MainWindow(QMainWindow):
    PAGE_MENU = 0
    PAGE_WORKSPACE = 1

    def __init__(self, app: QApplication, title: str) -> None:
        super().__init__()

        self._app = app
        self._title = title
        self.setMinimumSize(400, 300)
        self.setWindowTitle(self._title)
        self.setWindowIcon(QIcon(self._app.resource_loader.get("APP_ICON", "")))
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
            QToolTip {
                background-color: #F4EEFF;
                color: #424874;
                border: 1px solid #A6B1E1;
                border-radius: 5px;
                font-size: 10px;
                opacity: 230;
            }
        """)

        self._risk_files: list[File] = []
        self._current_tab_index: int = -1
        self._recent_files_manager = RecentFilesManager(self._app)
        self._action_handler = ActionHandler(self._app, self)

        self._autosave_timer = QTimer()
        self._autosave_timer.setInterval(300000)
        self._autosave_timer.timeout.connect(self._auto_save_files)
        self._autosave_timer.start()

        self._stacked_widget = QStackedWidget()
        self.setCentralWidget(self._stacked_widget)

        self._menu_page = MainMenuPage()
        self._menu_page.recent_files_grid.set_click_callback(self._on_recent_file_clicked)
        self._stacked_widget.addWidget(self._menu_page)

        self._workspace_page = WorkspacePage()
        self._workspace_page.tab_widget.tabCloseRequested.connect(self._close_risk_file)
        self._workspace_page.tab_widget.currentChanged.connect(self._switch_risk_map)
        self._stacked_widget.addWidget(self._workspace_page)

        self._setup_menu_bar()
        self.setStatusBar(QStatusBar(self))

        self._show_menu_page()

    def _setup_menu_bar(self) -> None:
        self._menu_bar = MenuBar()
        self.setMenuBar(self._menu_bar)

        file_menu_items = [
            MenuItem("Открыть", self._on_open, "Ctrl+O", "Открыть файл"),
            MenuItem("Новая карта", lambda: self._action_handler.on_new(RiskMapFile), "Ctrl+N", "Создать новый документ"),
            MenuItem("Новая сводная ведомость", lambda: self._action_handler.on_new(RiskSummaryFile), "Ctrl+Alt+N", "Создать новый документ"),
            MenuItem("Новая карта из шаблона", self._action_handler.on_new_from_template, "Ctrl+Shift+N", "Создать из шаблона"),
            MenuItem(None),
            MenuItem("Сохранить", self._action_handler.on_save, "Ctrl+S", "Сохранить текущий файл"),
            MenuItem("Сохранить как", self._action_handler.on_save_as, "Ctrl+Shift+S", "Сохранить в новый файл"),
            MenuItem(None),
            MenuItem("Экспортировать", self.on_export, "Ctrl+P", "Экспорт документа"),
            MenuItem(None),
            MenuItem("Выход", self.close, "Ctrl+Q", "Закрыть приложение"),
        ]
        self._menu_bar.add_menu("Файл", file_menu_items)

        help_menu_items = [
            MenuItem("О программе", self._action_handler.show_about, tooltip="Информация о приложении"),
            MenuItem("Руководство пользователя", self._action_handler.on_help, "F1"),
        ]
        self._menu_bar.add_menu("Справка", help_menu_items)

        self._workspace_page.tab_widget.currentChanged.connect(self.on_tab_changed)

    def on_export(self) -> None: ...

    def on_tab_changed(self, index):
        widget = self.tab_widget.widget(index)
        if isinstance(widget, RiskMapTab): self._menu_bar.set_export_for_risk_map()
        elif isinstance(widget, RiskSummaryTab): self._menu_bar.set_export_for_risk_summary()


    def _update_menu_state(self) -> None:
        has_file = self.current_risk_file is not None

        self._menu_bar.set_action_enabled("Сохранить", has_file)
        self._menu_bar.set_action_enabled("Сохранить как", has_file)
        self._menu_bar.set_export_enabled(has_file)

    def _show_menu_page(self) -> None:
        self._reload_recent_files()
        self._stacked_widget.setCurrentIndex(self.PAGE_MENU)
        self._update_menu_state()

    def show_workspace_page(self) -> None:
        self._stacked_widget.setCurrentIndex(self.PAGE_WORKSPACE)
        self._update_menu_state()

    def _reload_recent_files(self) -> None:
        self._menu_page.recent_files_grid.clear()
        for file_path in self._recent_files_manager.recent_files:
            icon_path = FileMapping.RECENT_FILES_ICONS.get(Path(file_path).suffix, "text-x-generic")
            icon = QIcon(normalize_path(icon_path))
            self._menu_page.recent_files_grid.add_item(file_path, icon)

    def _on_recent_file_clicked(self, file_path: str) -> None:
        if not Path(file_path).exists():
            self._recent_files_manager.remove_file(file_path)
            RusMsgBox.information(self, "Файл не найден",
                                  f'Файл "{Path(file_path).name}" был перемещён или удалён.')
            self._reload_recent_files()
            return

        self._open_file(file_path)

    def _open_file(self, file_path: str) -> None:
        if self.activate_tab_if_open(file_path):
            self.show_workspace_page()
            return

        risk_file_class = FileMapping.EXTENSIONS_TO_CLASSES.get(Path(file_path).suffix, None)
        if not risk_file_class: return

        risk_file = risk_file_class.load_from_file(app=self._app, open_path=file_path)
        if not risk_file: return

        self._recent_files_manager.add_file(file_path)
        self.add_risk_file_tab(risk_file)
        self.show_workspace_page()

    def add_risk_file_tab(self, risk_file: File) -> None:
        file_class = FileMapping.get_file_class(risk_file)

        existing_names = {rf.name for rf in self._risk_files}
        base_name = risk_file.name if risk_file.name else risk_file.DEFAULT_NAME
        new_name = base_name
        counter = 1
        while new_name in existing_names:
            new_name = f"{base_name} ({counter})"
            counter += 1
        risk_file.name = new_name

        self._risk_files.append(risk_file)
        tab_class = FileMapping.TABS_CLASSES.get(file_class, None)
        if not tab_class: return

        tab = tab_class(self._app, risk_file)
        self._workspace_page.tab_widget.addTab(tab, risk_file.tab_name if hasattr(risk_file, "tab_name") else "")

        new_index = len(self._risk_files) - 1
        self._workspace_page.tab_widget.setCurrentIndex(new_index)
        self._current_tab_index = new_index
        tab.update_form()
        self._update_menu_state()

    def activate_tab_if_open(self, file_path: str) -> bool:
        if not file_path: return False

        target = normalize_path(file_path)
        for index, risk_file in enumerate(self._risk_files):

            if risk_file.save_path:
                current = normalize_path(risk_file.save_path)

                if current == target:
                    self._workspace_page.tab_widget.setCurrentIndex(index)
                    self._current_tab_index = index
                    return True

        return False

    def _close_risk_file(self, index: int) -> None:
        if index < 0 or index >= len(self._risk_files): return

        target = self._risk_files[index]
        ext = FileMapping.CLASS_TO_EXTENSIONS.get(target.__class__, None)
        if not ext: return
        ext = ext["extension"]
        if hasattr(target, "is_modified") and target.is_modified:
            reply = RusMsgBox.question(self, 'Сохранение изменений',
                                       f'Сохранить изменения в карт "{target.name}{ext}" перед закрытием?')

            if reply == QMessageBox.StandardButton.Yes:
                self._current_tab_index = index
                self._on_save()

            elif reply == QMessageBox.StandardButton.No: pass
            else: return

        self._workspace_page.tab_widget.removeTab(index)
        del self._risk_files[index]

        if len(self._risk_files) == 0:
            for cls in FileMapping.EXTENSIONS_TO_CLASSES.values():
                cls.set_counter(0)
            self._current_tab_index = -1
            self._show_menu_page()
        else:
            self._current_tab_index = min(index, len(self._risk_files) - 1)
            self._workspace_page.tab_widget.setCurrentIndex(self._current_tab_index)

        self._update_menu_state()

    def _switch_risk_map(self, index: int) -> None:
        if index < 0 or index >= len(self._risk_files): return

        self._current_tab_index = index
        current_tab = self._workspace_page.tab_widget.widget(index)

        if current_tab and isinstance(current_tab, BaseTab):
            current_tab.update_form()

        self._update_menu_state()

    def _auto_save_files(self) -> None:
        for i, risk_file in enumerate(self._risk_files):
            if i != self._current_tab_index:
                if hasattr(risk_file, 'auto_save'): risk_file.auto_save()

    def create_new_file(self, file_type: type[TFile]) -> None:
        risk_file = file_type()
        self.add_risk_file_tab(risk_file)
        self.show_workspace_page()

    def _on_new_risk_map(self) -> None:
        risk_map = RiskMapFile(self._app)
        self.add_risk_file_tab(risk_map)
        self.show_workspace_page()

    def _on_new_risk_summary(self) -> None:
        risk_summary = RiskSummaryFile(self._app)
        self.add_risk_file_tab(risk_summary)
        self.show_workspace_page()

    def _on_new_map_from_template(self) -> None:
        template_path, _ = QFileDialog.getOpenFileName(self, "Выберите шаблон карты рисков", "templates",
                                                       "Файлы шаблонов (*.rskm)")

        if not template_path: return

        risk_map = RiskMapFile.load_from_file(app=self._app, open_path=template_path)
        if risk_map:
            risk_map._save_path = None
            risk_map._name = None
            self.add_risk_file_tab(risk_map)
            self.show_workspace_page()

    def _on_open(self) -> None:
        self._action_handler.on_open()

    def _on_save(self) -> None:
        self._action_handler.on_save()

    def _on_save_as(self) -> None:
        self._action_handler.on_save_as()

    def open_file_from_args(self, file_path: Path) -> None:
        self._open_file(str(file_path))

    @property
    def current_risk_file(self) -> Optional[File]:
        if 0 <= self._current_tab_index < len(self._risk_files):
            return self._risk_files[self._current_tab_index]
        return None

    @property
    def risk_files(self) -> list[File]:
        return self._risk_files

    @property
    def risk_maps_len(self) -> int:
        return len(self._risk_files)

    @property
    def tab_widget(self) -> QTabWidget:
        return self._workspace_page.tab_widget

    @property
    def current_file_index(self) -> int:
        return self._current_tab_index

    @current_file_index.setter
    def current_file_index(self, value: int) -> None:
        self._current_tab_index = value

    @property
    def recent_files_manager(self) -> RecentFilesManager:
        return self._recent_files_manager