from src.core.converters.strategy import RiskMapConverterStrategy
from src.core.file_system import TFile
from src.models.risk_map import RiskMapFile
from src.models.risk_summary import RiskSummaryFile
from src.ui.components.risk_map_form import RiskAnalysisMainForm
from src.ui.components.risk_summary_form import RiskSummaryMainForm
from src.ui.components.rus_msg_box import RusMsgBox

from pathlib import Path
from PySide6.QtGui import Qt, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidgetItem, QFileDialog, QApplication
from typing import Generic


class BaseTab(QWidget, Generic[TFile]):
    def __init__(self, file: TFile, parent=None) -> None:
        super().__init__(parent)

        self.file = file
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

    def update_form(self) -> None: ...


class RiskMapTab(BaseTab[RiskMapFile]):
    def __init__(self, app: QApplication, risk_map: RiskMapFile) -> None:
        super().__init__(risk_map)
        self._app = app
        self.file = risk_map
        self.form = RiskAnalysisMainForm(app=self._app, risk_map=self.file)

        self._layout.addWidget(self.form)

        self.form.button_calculate.clicked.connect(self.on_calc_button_clicked)
        self.form.button_convert_to.clicked.connect(self.on_convert_button_clicked)
        self.update_form()

    def on_calc_button_clicked(self) -> None:
        if not self.file: return

        result = self.file.calculate()

        if result == 0x1:
            if self.form and self.form.methods_data_table_widget:
                self.form.button_calculate.pulse(color=QColor("#2ecc71"), fade_in=80, fade_out=720)
                self.update_form()

        elif result == 0x0:
            self.form.button_calculate.pulse(color=QColor("#e74c3c"), fade_in=80, fade_out=720)
            RusMsgBox.information(self, "Ошибка расчета", "Не все обязательные поля заполнены.")

        else:
            self.form.button_calculate.pulse(color=QColor("#e74c3c"), fade_in=80, fade_out=720)
            RusMsgBox.information(self, "Ошибка расчета", "Нет данных для расчета.")

    def on_convert_button_clicked(self) -> None:
        if not self.file: return

        result = self.file.calculate(update_methods=False)
        self.file.is_modified = False
        if result == 0x0:
            RusMsgBox.information(self, "Ошибка конвертирования", "Заполнены не все обязательные поля.")
            return
        if result != 0x1:
            RusMsgBox.information(self, "Ошибка конвертирования", "Нет данных для расчета.")
            return

        default_name = self.file.name
        save_path, _filter = QFileDialog.getSaveFileName(self, "Сохранить файл отчета", default_name,
                                                         RiskMapConverterStrategy.get_all_filters())

        if not save_path: return

        converter = RiskMapConverterStrategy(self._app).create_converter(_filter, self.file)
        if not converter:
            RusMsgBox.warning(self, "Ошибка", "Неподдерживаемый формат файла.")
            return
        try:
            converter.convert(Path(save_path))
        except PermissionError:
            RusMsgBox.information(self, "Ошибка сохранения", f"Файл {save_path} недоступен для перезаписи.\n"
                                                             f"Закройте файл и повторите попытку.")
        except Exception as e:
            RusMsgBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def update_form(self) -> None:
        if not self.form or not self.file:
            return

        self.form.setQLineBlockSignals(True)
        self.form.mapNo_text = self.file.map_no or ""
        self.form.profession_text = self.file.profession or ""
        self.form.structure_division_text = self.file.department or ""
        self.form.work_description_text = self.file.description or ""
        self.form.used_materials_text = self.file.tools_and_materials or ""
        self.form.chairman_fullname_text = self.file.chairman or ""

        if self.file.result_str:
            self.form.summary_risk_level_text = (str(round(self.file.prof_risk, 2)) if self.file.prof_risk else "")
            self.form.summary_risk_indicator_text = (str(self.file.k_factor) if self.file.k_factor else str(0.0))
            self.form.summary_risk_final_level_text = (str(round(self.file.result, 2)) if self.file.result else "")
            self.form.summary_risk_classification_text = self.file.result_str

        self.form.setQLineBlockSignals(False)

        self.form.risk_data_table_widget.setRowCount(0)
        for record in self.file.table:
            row = self.form.risk_data_table_widget.rowCount()
            self.form.risk_data_table_widget.insertRow(row)

            remove_btn = QPushButton('-')
            remove_btn.setObjectName('ManageRowButtonDelete')
            remove_btn.clicked.connect(self.form.risk_data_table_widget.on_remove_row_clicked)
            self.form.risk_data_table_widget.setCellWidget(row, 0, remove_btn)

            n = QTableWidgetItem(str(row + 1))
            n.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_data_table_widget.setItem(row, 1, n)

            danger = QTableWidgetItem(f"{record.n}. {record.danger}" if (record.n and record.danger) else "")
            danger.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_data_table_widget.setItem(row, 2, danger)

            event = QTableWidgetItem(f"{record.n_} {record.event}" if (record.n_ and record.event) else "")
            event.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_data_table_widget.setItem(row, 3, event)

            for col, attr in [(4, "damage"), (5, "susceptibility"), (6, "probability"), (7, "rating")]:
                item = QTableWidgetItem(getattr(record, attr, ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
                self.form.risk_data_table_widget.setItem(row, col, item)

        self.form.risk_data_table_widget.initialize_default_row()

        if self.file.method_modified:
            self.form.methods_data_table_widget.setRowCount(0)
            for method in self.file.methods:
                row = self.form.methods_data_table_widget.rowCount()
                self.form.methods_data_table_widget.insertRow(row)

                remove_btn = QPushButton('-')
                remove_btn.setObjectName('ManageRowButton')
                remove_btn.clicked.connect(self.form.methods_data_table_widget.on_remove_method_clicked)
                self.form.methods_data_table_widget.setCellWidget(row, 0, remove_btn)

                item = QTableWidgetItem(method)
                item.setFlags(Qt.ItemFlag.NoItemFlags)
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                self.form.methods_data_table_widget.setItem(row, 1, item)

            self.form.methods_data_table_widget.update_height()
            self.form.methods_data_table_widget.update_height()
            self.file._method_modified = False


class RiskSummaryTab(BaseTab[RiskSummaryFile]):
    def __init__(self, app: QApplication, risk_summary: RiskSummaryFile) -> None:
        super().__init__(risk_summary)
        self._app = app
        self.file = risk_summary
        self.form = RiskSummaryMainForm(app=self._app, risk_summary=self.file)

        self._layout.addWidget(self.form)

        self.form.button_generate_report.clicked.connect(self.on_convert_button_clicked)
        self.update_form()

    def on_convert_button_clicked(self) -> None:
        if not self.file: return

        self.file.is_modified = False
        if not all(entry.is_filled for entry in self.file.entries_table):
            RusMsgBox.information(self, "Ошибка конвертирования", "Недостаточно данных для конвертации.")
            return

        default_name = self.file.name
        save_path, _filter = QFileDialog.getSaveFileName(self, "Сохранить файл отчета", default_name,
                                                         RiskMapConverterStrategy.get_all_filters())

        if not save_path: return

        converter = RiskMapConverterStrategy(self._app).create_converter(_filter, self.file)
        if not converter:
            RusMsgBox.warning(self, "Ошибка", "Неподдерживаемый формат файла.")
            return
        try:
            converter.convert(Path(save_path))
        except PermissionError:
            RusMsgBox.information(self, "Ошибка сохранения", f"Файл {save_path} недоступен для перезаписи.\n"
                                                             f"Закройте файл и повторите попытку.")
        except Exception as e:
            RusMsgBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def update_form(self) -> None:
        if not self.form or not self.file:
            return

        self.form.setQLineBlockSignals(True)
        self.form.org_name_text = self.file.org_name or ""
        self.form.address_text = self.file.address or ""
        self.form.position_text = self.file.position or ""
        self.form.ceo_text = self.file.ceo or ""
        self.form.inn_text = self.file.inn or ""
        self.form.okved_text = self.file.okved or ""
        self.form.okato_text = self.file.okato or ""
        self.form.chairman_text = self.file.chairman or ""

        self.form.setQLineBlockSignals(False)

        self.form.risk_summary_table_widget.setRowCount(0)
        for entry in self.file.entries_table:
            row = self.form.risk_summary_table_widget.rowCount()
            self.form.risk_summary_table_widget.insertRow(row)

            remove_btn = QPushButton('-')
            remove_btn.setObjectName('ManageRowButtonDelete')
            remove_btn.clicked.connect(self.form.risk_summary_table_widget.on_remove_row_clicked)
            self.form.risk_summary_table_widget.setCellWidget(row, 0, remove_btn)

            n = QTableWidgetItem(str(row + 1))
            n.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_summary_table_widget.setItem(row, 1, n)

            workplace_no = QTableWidgetItem(entry.workplace_no if entry.workplace_no else "")
            workplace_no.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_summary_table_widget.setItem(row, 2, workplace_no)

            profession = QTableWidgetItem(entry.profession if entry.profession else "")
            profession.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_summary_table_widget.setItem(row, 3, profession)

            result = QTableWidgetItem(f"{entry.result:.2f}" if entry.result is not None else "")
            result.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_summary_table_widget.setItem(row, 4, result)

            classification = QTableWidgetItem(entry.classification if entry.classification else "")
            classification.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignHCenter)
            self.form.risk_summary_table_widget.setItem(row, 5, classification)


        self.form.risk_summary_table_widget.initialize_default_row()
