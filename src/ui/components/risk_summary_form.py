from src.models.risk_summary import RiskSummaryFile, Entry
from src.models.risk_map import RiskMapFile
from src.ui.styles.qss_styles import Styles

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTableWidgetItem, \
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QTableWidget, QFileDialog, QMessageBox, QDialog, QListWidget, \
    QDialogButtonBox, QApplication


class MissingPathsDialog(QDialog):
    def __init__(self, app: QApplication, missing_entries: list[dict], parent=None):
        super().__init__(parent)
        self._app = app
        self.missing_entries = missing_entries
        self.resolved_paths = {}
        self.skipped_entries = []

        self.setWindowTitle("Отсутствующие файлы")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        self.setStyleSheet("""
        QDialog {
            background-color: #F4EEFF;
        }
        QMessageBox QLabel {
            background-color: #F4EEFF;
            color: #4a4a7d;
            font-size: 14px;
            text-align: center;
        }
        """)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        info_label = QLabel("Следующие файлы были удалены или перемещены:")
        info_label.setStyleSheet("font-weight: bold; color: #424874;")
        layout.addWidget(info_label)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #F4EEFF;
                border: 2px solid #424874;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                color: #424874;
            }
            QListWidget::item:selected {
                background-color: #A6B1E1;
            }
        """)

        for entry in self.missing_entries:
            workplace_no = entry.get("n", "Неизвестно")
            profession = entry.get("profession", "Неизвестно")
            result = entry.get("result", "Неизвестно")
            classification = entry.get("classification", "Неизвестно")

            path = entry.get('path', 'Неизвестно')
            self.list_widget.addItem(f"{path}:\t{workplace_no} - {profession} - {result} - {classification}")

        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()

        self.btn_locate = QPushButton("Указать новый путь")
        self.btn_locate.setStyleSheet("""
            QPushButton {
                background-color: #5a67d8;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c51bf;
            }
        """)
        self.btn_locate.clicked.connect(self._on_locate_clicked)

        self.btn_skip = QPushButton("Пропустить")
        self.btn_skip.setStyleSheet("""
            QPushButton {
                background-color: #A6B1E1;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8a9cf3;
            }
        """)
        self.btn_skip.clicked.connect(self._on_skip_clicked)

        self.btn_skip_all = QPushButton("Пропустить все")
        self.btn_skip_all.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_skip_all.clicked.connect(self._on_skip_all_clicked)

        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_locate)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_skip)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_skip_all)
        btn_layout.addStretch(1)

        layout.addLayout(btn_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

    def _on_locate_clicked(self):
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Выбор файла", "Выберите запись из списка")
            return

        entry: dict = self.missing_entries[current_row]
        entry_checksum = entry.get("checksum", "")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл карты оценки рисков",
            "",
            "Файлы карт профессиональных рисков (*.rskm)"
        )

        if file_path:
            try:
                risk_map = RiskMapFile.load_from_file(self._app, file_path)
                if risk_map:
                    found_checksum = Entry.get_stored_checksum(risk_map)
                    if found_checksum != entry_checksum: return

                    old_path = entry.get('path', '')
                    self.resolved_paths[old_path] = file_path

                    self.list_widget.takeItem(current_row)
                    self.missing_entries.pop(current_row)

                    if self.list_widget.count() == 0:
                        QMessageBox.information(self, "Готово", "Все новые пути указаны")
                        self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось загрузить файл")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")

    def _on_skip_clicked(self):
        current_row = self.list_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите запись из списка")
            return

        entry = self.missing_entries[current_row]
        self.skipped_entries.append(entry)

        self.list_widget.takeItem(current_row)
        self.missing_entries.pop(current_row)

        if self.list_widget.count() == 0:
            self.accept()

    def _on_skip_all_clicked(self):
        self.skipped_entries.extend(self.missing_entries)
        self.missing_entries.clear()
        self.accept()


class RiskSummaryTableHorizontalHeaderView(QHeaderView):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.geometriesChanged.connect(self._on_geometries_changed)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        self.setMinimumSize(400, 300)

    def _on_geometries_changed(self) -> None:
        max_size = -1
        fm = self.fontMetrics()
        model = self.model()

        for i in range(self.count()):
            size = self.sectionSize(i)
            text = model.headerData(i, self.orientation(), Qt.ItemDataRole.DisplayRole)
            rect = fm.boundingRect(0, 0, size, 0, Qt.TextFlag.TextWordWrap, text)
            max_size = max(max_size, rect.height())

        if max_size >= 0:
            self.setFixedHeight(int(max_size * 1.2))


class RiskSummaryTable(QTableWidget):
    _COLUMN_NAMES = [
        '',
        '№ п/п',
        'Номер рабочего места',
        'Наименование профессии (должности)',
        'Уровень профессионального риска',
        'Классификация',
    ]
    def __init__(self, app: QApplication, parent: QWidget, risk_summary: RiskSummaryFile) -> None:

        super().__init__(1, len(self._COLUMN_NAMES), parent)
        self._app = app
        self.risk_summary = risk_summary
        self._setup_ui()
        self._setup_connections()
        self._load_existing_entries()
        self.initialize_default_row()

    def _setup_ui(self) -> None:
        self.setStyleSheet("""
            height: 60px;
            color: #424874;
            border-color: #424874;
            border: 1px solid #424874
        """)
        self.verticalHeader().setDefaultSectionSize(30)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setHorizontalHeader(RiskSummaryTableHorizontalHeaderView(self))
        self.setHorizontalHeaderLabels(self._COLUMN_NAMES)
        self.setStyleSheet(Styles.TABLE)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.verticalHeader().hide()
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        widths = [40, 65, 200, 500, 300, 200]

        for col, wid in enumerate(widths):
            self.setColumnWidth(col, wid)

        self.setMinimumHeight(150)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def _setup_connections(self) -> None:
        pass

    def _load_existing_entries(self) -> None:
        for entry in self.risk_summary.entries_table:
            self._add_entry_row(entry)
        self.update_custom_numbering()
        self.update_height()

    def initialize_default_row(self) -> None:
        row = self.rowCount()
        self.insertRow(row)

        add_button = QPushButton('+')
        add_button.setObjectName('ManageRowButtonAdd')
        add_button.clicked.connect(self.add_row)
        self.setCellWidget(row, 0, add_button)

        for col in range(1, len(self._COLUMN_NAMES)):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.setItem(row, col, item)

        self.update_custom_numbering()
        self.update_height()

    def add_row(self) -> None:
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Выберите файлы карты оценки рисков", "",
                                                     "Файлы карт профессиональных рисков (*.rskm)")

        if not file_paths:
            return

        for file_path in file_paths:
            try:
                risk_map = RiskMapFile.load_from_file(self._app, file_path)
                if risk_map:
                    existing_checksum = Entry.get_stored_checksum(risk_map)
                    if any(e.checksum == existing_checksum for e in self.risk_summary.entries_table):
                        QMessageBox.information(self, "Предупреждение", "Эта карта уже добавлена в сводную ведомость")
                        return

                    self.risk_summary.add_entry(risk_map)
                    entry = self.risk_summary.entries_table[-1]

                    row_index = self.rowCount() - 1
                    self.insertRow(row_index)

                    self._populate_entry_row(row_index, entry)

                    self.update_custom_numbering()
                    self.update_height()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось загрузить файл")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при загрузке файла: {str(e)}")

    def _add_entry_row(self, entry: Entry) -> None:
        row_index = self.rowCount() - 1
        self.insertRow(row_index)
        self._populate_entry_row(row_index, entry)
        self.update_height()

    def _populate_entry_row(self, row_index: int, entry: Entry) -> None:
        remove_button = QPushButton('-')
        remove_button.setObjectName('ManageRowButtonDelete')
        remove_button.clicked.connect(self.on_remove_row_clicked)
        self.setCellWidget(row_index, 0, remove_button)

        num_item = QTableWidgetItem(str(row_index + 1))
        num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        num_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.setItem(row_index, 1, num_item)

        workplace_item = QTableWidgetItem(entry.workplace_no)
        workplace_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        workplace_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.setItem(row_index, 2, workplace_item)

        profession_item = QTableWidgetItem(entry.profession)
        profession_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        profession_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.setItem(row_index, 3, profession_item)

        result_item = QTableWidgetItem(str(entry.result) if entry.result else "")
        result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        result_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.setItem(row_index, 4, result_item)

        classification_item = QTableWidgetItem(entry.classification)
        classification_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        classification_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
        self.setItem(row_index, 5, classification_item)

    def on_remove_row_clicked(self) -> None:
        button = self.sender()
        if button:
            for row in range(self.rowCount() - 1):
                if self.cellWidget(row, 0) == button:
                    self.risk_summary.remove_entry(row)
                    self.removeRow(row)
                    break

        self.update_custom_numbering()
        self.update_height()

    def update_height(self) -> None:
        row_height = self.rowHeight(0) if self.rowCount() > 0 else 30
        total_height = (self.rowCount() * row_height) + self.horizontalHeader().height() + 2
        min_height = 100
        max_height = 600
        self.setFixedHeight(max(min_height, min(total_height, max_height)))

    def update_custom_numbering(self) -> None:
        for row in range(self.rowCount() - 1):
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.setItem(row, 1, num_item)

    def refresh_table(self) -> None:
        while self.rowCount() > 1:
            self.removeRow(0)

        self._load_existing_entries()


class RiskSummaryMainForm(QWidget):
    def __init__(self, app: QApplication, risk_summary: RiskSummaryFile, parent=None) -> None:
        super().__init__(parent)
        self._app = app
        self.risk_summary = risk_summary
        self.setStyleSheet(Styles.SCROLL_AREA)

        self._init_scroll_area()
        self._init_title_section()
        self._init_metadata_section()
        self._init_tables()
        self._init_buttons()
        self._assemble_layout()
        self._setup_line_edit_connections()
        self._load_data()
        self._handle_missing_and_invalid_entries()

    def _init_title_section(self) -> None:
        self._title_frame = QFrame(self._content_widget)
        self._title_frame.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #424874;
            }
        """)

        layout = QHBoxLayout(self._title_frame)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel('Сводная ведомость результатов оценки уровней профессиональных рисков', self._title_frame), alignment=Qt.AlignmentFlag.AlignCenter)

    def _init_scroll_area(self) -> None:
        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.addWidget(self._scroll_area)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet("background-color: #F4EEFF;")

        self._content_widget = QWidget(self._scroll_content)
        self._content_widget.setStyleSheet("background-color: #F4EEFF;")


    def _init_metadata_section(self) -> None:
        inner_frame = QFrame(self._content_widget)
        inner_frame.setStyleSheet("""
            QFrame {
                background-color: #E9E4FF;
                border-radius: 20px;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #424874;
            }
            QLineEdit {
                font-size: 16px;
                color: #424874;
                background-color: #E9E4FF;
                border: 0;
                border-bottom: 2px solid #424874;
                border-radius: 0;
            }
        """)

        inner_layout = QVBoxLayout(inner_frame)
        inner_layout.setSpacing(1)
        inner_layout.setContentsMargins(20, 20, 20, 20)

        fields = [
            ("_orgNameTextEdit", "Наименование организации"),
            ("_addressTextEdit", "Адрес организации"),
            ("_positionTextEdit", "Должность руководителя"),
            ("_ceoTextEdit", "ФИО руководителя"),
            ("_innTextEdit", "ИНН"),
            ("_okvedTextEdit", "ОКВЭД"),
            ("_okatoTextEdit", "ОКАТО"),
            ("_chairmanTextEdit", "ФИО председателя комиссии"),
        ]

        for attr_name, label_text in fields:
            edit = QLineEdit('', inner_frame)
            edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            setattr(self, attr_name, edit)

            inner_layout.addWidget(edit)
            inner_layout.addWidget(QLabel(label_text, inner_frame),
                                   alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._metadata_outer_frame = QFrame(self._content_widget)
        outer_layout = QHBoxLayout(self._metadata_outer_frame)
        outer_layout.addStretch(1)
        outer_layout.addWidget(inner_frame, 2)
        outer_layout.addStretch(1)

    def _init_tables(self) -> None:
        self.risk_summary_table_widget = RiskSummaryTable(app=self._app, parent=self, risk_summary=self.risk_summary)

    def _init_buttons(self) -> None:
        self._buttons_widget = QWidget()
        self._buttons_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._buttons_widget.setStyleSheet("""
            QPushButton {
                background-color: #383e92;
                border-radius: 20px;
                color: #F4EEFF;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#GenerateReportButton {
                background-color: #383e92;
            }
            QPushButton#GenerateReportButton:hover {
                background-color: #241d50;
            }
        """)

        self.button_generate_report = QPushButton('Сформировать отчет', parent=self._buttons_widget)
        self.button_generate_report.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_generate_report.setObjectName('GenerateReportButton')

        layout = QHBoxLayout(self._buttons_widget)
        layout.setSpacing(20)
        layout.addStretch()
        layout.addWidget(self.button_generate_report)
        layout.addStretch()

    def _assemble_layout(self) -> None:
        dividers = [self._create_divider() for _ in range(2)]

        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setContentsMargins(20, 0, 20, 20)
        content_layout.setSpacing(5)

        content_layout.addWidget(self._title_frame)
        content_layout.addWidget(dividers[0])

        content_layout.addSpacing(15)
        content_layout.addWidget(self._metadata_outer_frame)
        content_layout.addWidget(dividers[1])

        content_layout.addSpacing(10)
        content_layout.addWidget(self.risk_summary_table_widget)

        content_layout.addStretch(1)

        scroll_layout = QVBoxLayout(self._scroll_content)
        scroll_layout.addWidget(self._content_widget)
        scroll_layout.addWidget(self._buttons_widget)

        self._scroll_area.setWidget(self._scroll_content)

    @staticmethod
    def _create_divider() -> QFrame:
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        divider.setStyleSheet("border: 4px solid #A6B1E1;")
        return divider

    def _setup_line_edit_connections(self):
        field_map = {
            self._orgNameTextEdit: "org_name",
            self._addressTextEdit: "address",
            self._positionTextEdit: "position",
            self._ceoTextEdit: "ceo",
            self._innTextEdit: "inn",
            self._okvedTextEdit: "okved",
            self._okatoTextEdit: "okato",
            self._chairmanTextEdit: "chairman",
        }

        for edit, attr in field_map.items():
            edit.textChanged.connect(self._make_field_handler(attr))

    def _make_field_handler(self, model_attr: str):
        def handler(text: str):
            if self.risk_summary:
                setattr(self.risk_summary, model_attr, text)

        return handler

    def _load_data(self) -> None:
        self.setQLineBlockSignals(True)

        self._orgNameTextEdit.setText(self.risk_summary.org_name)
        self._addressTextEdit.setText(self.risk_summary.address)
        self._positionTextEdit.setText(self.risk_summary.position)
        self._ceoTextEdit.setText(self.risk_summary.ceo)
        self._innTextEdit.setText(self.risk_summary.inn)
        self._okvedTextEdit.setText(self.risk_summary.okved)
        self._okatoTextEdit.setText(self.risk_summary.okato)
        self._chairmanTextEdit.setText(self.risk_summary.chairman)

        self.setQLineBlockSignals(False)

    def _handle_missing_and_invalid_entries(self):
        if self.risk_summary.missing_paths_entries:
            dialog = MissingPathsDialog(self._app, self.risk_summary.missing_paths_entries.copy(), self)
            dialog.exec()

            for old_path, new_path in dialog.resolved_paths.items():
                try:
                    risk_map = RiskMapFile.load_from_file(self._app, new_path)
                    if risk_map: self.risk_summary.add_entry(risk_map)
                except Exception as e: pass

                for entry in self.risk_summary.entries_table:
                    if entry.reference_path == old_path:
                        entry.reference_path = new_path
                        risk_map = RiskMapFile.load_from_file(self._app, new_path)
                        if risk_map:
                            entry.sync(risk_map)

            self.risk_summary.skip_all_missing_paths()

        self.risk_summary_table_widget.refresh_table()

    def setQLineBlockSignals(self, flag: bool):
        edits = [
            self._orgNameTextEdit,
            self._addressTextEdit,
            self._positionTextEdit,
            self._ceoTextEdit,
            self._innTextEdit,
            self._okvedTextEdit,
            self._okatoTextEdit,
            self._chairmanTextEdit,
        ]
        for edit in edits:
            edit.blockSignals(flag)

    @property
    def org_name_text(self) -> str:
        return self._orgNameTextEdit.text()

    @org_name_text.setter
    def org_name_text(self, value: str) -> None:
        self._orgNameTextEdit.setText(value)

    @property
    def address_text(self) -> str:
        return self._addressTextEdit.text()

    @address_text.setter
    def address_text(self, value: str) -> None:
        self._addressTextEdit.setText(value)

    @property
    def position_text(self) -> str:
        return self._positionTextEdit.text()

    @position_text.setter
    def position_text(self, value: str) -> None:
        self._positionTextEdit.setText(value)

    @property
    def ceo_text(self) -> str:
        return self._ceoTextEdit.text()

    @ceo_text.setter
    def ceo_text(self, value: str) -> None:
        self._ceoTextEdit.setText(value)

    @property
    def inn_text(self) -> str:
        return self._innTextEdit.text()

    @inn_text.setter
    def inn_text(self, value: str) -> None:
        self._innTextEdit.setText(value)

    @property
    def okved_text(self) -> str:
        return self._okvedTextEdit.text()

    @okved_text.setter
    def okved_text(self, value: str) -> None:
        self._okvedTextEdit.setText(value)

    @property
    def okato_text(self) -> str:
        return self._okatoTextEdit.text()

    @okato_text.setter
    def okato_text(self, value: str) -> None:
        self._okatoTextEdit.setText(value)

    @property
    def chairman_text(self) -> str:
        return self._chairmanTextEdit.text()

    @chairman_text.setter
    def chairman_text(self, value: str) -> None:
        self._chairmanTextEdit.setText(value)