from src.core.file_system import TFile
from src.models.risk_map import RiskMapFile
from src.utils.file_mapping import FileMapping
from src.utils.utils import normalize_path

from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QApplication
import sys, os, webbrowser


class ActionHandler:
    _HELP_URL = os.getenv("HELP_URL")

    def __init__(self, app: QApplication, parent) -> None:
        self._app = app
        self._parent = parent

    def on_help(self) -> None:
        if not self._HELP_URL: return
        webbrowser.open_new(self._HELP_URL)

    def show_about(self) -> None: ...

    def on_new(self, file_type: type[TFile]) -> None:
        self._parent.create_new_file(file_type=file_type)

    def on_new_from_template(self) -> None:
        if getattr(sys, 'frozen', False): temp_dir = Path(sys.executable).parent / "templates"
        else: temp_dir = Path(__file__).parent.parent.parent / "templates"

        if not temp_dir.exists(): os.mkdir(temp_dir)

        template_path, _ = QFileDialog.getOpenFileName(
            parent=self._parent,
            caption="Выберите шаблон карты рисков",
            dir=str(temp_dir),
            filter="Файлы шаблонов (*.rskm)"
        )

        if template_path:
            risk_map = RiskMapFile.load_from_file(self._app, open_path=template_path)
            if risk_map:
                risk_map.save_path = None
                risk_map._name = None
                self._parent.add_risk_file_tab(risk_map)
                self._parent.show_workspace_page()

    def on_open(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            parent=self._parent,
            caption="Открыть файл карты рисков",
            dir="",
            filter="Все поддерживаемые файлы (*.rskm *.rsks);;Карты рисков (*.rskm);;Сводные ведомости (*.rsks)"
        )

        if not file_path: return

        if self._parent.activate_tab_if_open(file_path):
            self._parent.show_workspace_page()
            return

        risk_file_class = FileMapping.EXTENSIONS_TO_CLASSES.get(Path(file_path).suffix)
        if not risk_file_class: return

        risk_file = risk_file_class.load_from_file(open_path=file_path)

        if risk_file:
            risk_file.is_modified = False
            self._parent.recent_files_manager.add_file(file_path)
            self._parent.add_risk_file_tab(risk_file)
            self._parent.show_workspace_page()

    def on_save(self) -> None:
        current_file = self._parent.current_risk_file

        if not current_file: return

        if not current_file.save_path:
            self.on_save_as()
            return

        save_path = normalize_path(current_file.save_path)
        current_file.save_to_file(save_path=save_path)

        if hasattr(self._parent, "recent_files_manager") and self._parent.recent_files_manager:
            self._parent.recent_files_manager.add_file(save_path)
        self._parent.tab_widget.setTabText(self._parent.current_file_index, current_file.tab_name)

    def on_save_as(self) -> None:
        current_file = self._parent.current_risk_file
        if not current_file: return

        mapping = FileMapping.CLASS_TO_EXTENSIONS.get(current_file.__class__, None)
        if not mapping: return
        extension, filter_str = mapping["extension"], mapping["filter"]

        default_name = current_file.name
        save_path, _ = QFileDialog.getSaveFileName(
            parent=self._parent,
            caption="Сохранить файл карты",
            dir=default_name,
            filter=filter_str,
        )
        if not save_path: return

        if not save_path.lower().endswith(extension): save_path += extension

        current_file.name = Path(save_path).stem
        current_file.save_path = save_path
        current_file.save_to_file(save_path=save_path)

        if hasattr(self._parent, "recent_files_manager") and self._parent.recent_files_manager:
            self._parent.recent_files_manager.add_file(save_path)
        self._parent.tab_widget.setTabText(self._parent.current_file_index, current_file.tab_name)