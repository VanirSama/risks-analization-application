from src.core.database.manager import DatabaseManager
from src.models.risk_map import RiskMapFile, Record
from src.ui.components.animations import PulsingButton
from src.ui.components.delegates import ComboBoxDelegate
from src.ui.styles.qss_styles import Styles

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHeaderView, QLineEdit, QPushButton, QScrollArea, QSizePolicy, \
QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QTableWidget, QApplication


class RiskDataTableHorizontalHeaderView(QHeaderView):
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


class RiskDataTable(QTableWidget):
    _COLUMN_NAMES = [
        '',
        '№ п/п',
        'Опасность',
        'Опасное событие',
        'Качественное значение тяжести ущерба',
        'Качественное значение подверженности опасности',
        'Качественное значение вероятности возникновения опасности',
        'Оценка значимости риска по отдельной опасности',
    ]

    def __init__(self, app: QApplication, parent: QWidget, risk_map: RiskMapFile) -> None:

        super().__init__(1, len(self._COLUMN_NAMES), parent)
        self._app = app
        self.risk_map = risk_map
        self._setup_ui()
        self._setup_connections()

        for column in range(2, 8):
            self.setItemDelegateForColumn(column, ComboBoxDelegate(self))

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
        self.setHorizontalHeader(RiskDataTableHorizontalHeaderView(self))
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

        columns = range(0, 8)
        widths = [40, 65, 450, 450, 200, 190, 200, 230]

        for col, wid in zip(columns, widths):
            self.setColumnWidth(col, wid)

        self.setFixedHeight(100)

        self.setEditTriggers(QTableWidget.EditTrigger.CurrentChanged | QTableWidget.EditTrigger.SelectedClicked)

    def mouse_press_event(self, event) -> None:
        index = self.indexAt(event.pos())

        if index.isValid() and index.column() in (2, 3, 4, 5, 6):
            if index.row() < self.rowCount() - 1:
                super().mousePressEvent(event)
                self.edit(index)
                return

        super().mousePressEvent(event)

    def _setup_connections(self) -> None:
        self.cellChanged.connect(self._on_cell_changed)

    def _on_cell_changed(self,  row, column) -> None:
        if row == self.rowCount() - 1: return
        if column == 2: self._update_danger(row)
        elif column == 3: self._update_event(row)
        elif column in (4, 5, 6): self._update_risk_params(row)

    def _update_danger(self, row: int) -> None:
        danger_item = self.item(row, 2)
        if not danger_item: return

        danger = danger_item.text()
        self.setItem(row, 3, QTableWidgetItem(""))
        self.setItem(row, 4, QTableWidgetItem(""))
        self.setItem(row, 5, QTableWidgetItem(""))
        self.setItem(row, 6, QTableWidgetItem(""))

        if danger in self._app.database_manager.dangers:
            self.item(row, 2).setText(danger)
            record = self._get_or_create_record(row)
            record.danger = danger

        else: self.item(row, 2).setText("")

        self.risk_map.mark_modified()

    def _update_event(self, row) -> None:
        event_item = self.item(row, 3)
        danger_item = self.item(row, 2)

        if not event_item or not danger_item: return

        event = event_item.text()
        danger = danger_item.text()
        if danger in self._app.database_manager.dangers and event in self._app.database_manager.get_events(danger):
            record = self._get_or_create_record(row)
            record.event = event

        else:
            self.setItem(row, 4, QTableWidgetItem(""))
            self.setItem(row, 5, QTableWidgetItem(""))
            self.setItem(row, 6, QTableWidgetItem(""))
        self.risk_map.mark_modified()

    def _update_risk_params(self, row) -> None:
        for col in range(4, 7):
            if not self.item(row, col) or not self.item(row, col).text(): return

        record = self._get_or_create_record(row)
        damage = self.item(row, 4).text()
        if damage in DatabaseManager.DAMAGE.keys(): record.damage = damage

        susceptibility = self.item(row, 5).text()
        if susceptibility in DatabaseManager.SUSCEPTIBILITY.keys(): record.susceptibility = susceptibility

        probability = self.item(row, 6).text()
        if probability in DatabaseManager.PROBABILITY.keys(): record.probability = probability

        self.risk_map._isModified = True

    def _get_or_create_record(self, row) -> Record:
        if row >= len(self.risk_map.table):
            self.risk_map.add_record()
        return self.risk_map.table[row]

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

            if col == 1 or col == 7: item.setFlags(Qt.ItemFlag.NoItemFlags)
            else: item.setFlags(Qt.ItemFlag.ItemIsEnabled)

            self.setItem(row, col, item)

        self.update_custom_numbering()
        self.update_height()

    def add_row(self) -> None:
        row_index = self.rowCount() - 1
        self.insertRow(row_index)
        self.risk_map.add_record()

        remove_button = QPushButton('-')
        remove_button.setObjectName('ManageRowButtonDelete')
        remove_button.clicked.connect(self.on_remove_row_clicked)
        self.setCellWidget(row_index, 0, remove_button)

        for col in range(1, len(self._COLUMN_NAMES)):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, Qt.TextFlag.TextWordWrap)

            if col == 1 or col == 7: item.setFlags(Qt.ItemFlag.NoItemFlags)
            else: item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)

            self.setItem(row_index, col, item)

        self.update_custom_numbering()
        self.update_height()

    def on_remove_row_clicked(self) -> None:
        button = self.sender()
        if button:
            for row in range(self.rowCount() - 1):
                if self.cellWidget(row, 0) == button:
                    self.removeRow(row)
                    if row < len(self.risk_map.table):
                        self.risk_map.remove_record(row)
                    break

        self.update_custom_numbering()
        self.update_height()
        self.risk_map.mark_modified()

    def update_height(self) -> None:
        row_height = self.rowHeight(0) if self.rowCount() > 0 else 30
        total_height = (self.rowCount() * row_height) + self.horizontalHeader().height() + 2
        self.setFixedHeight(total_height)

    def update_custom_numbering(self) -> None:
        for row in range(self.rowCount() - 1):
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.setItem(row, 1, num_item)


class MethodsTable(QTableWidget):
    def __init__(self, app: QApplication, parent: QWidget, risk_map: RiskMapFile) -> None:
        self._column_names = ['', 'Общие меры по управлению рисками']

        super().__init__(1, len(self._column_names), parent)
        self._app = app
        self.risk_map = risk_map
        self.initialize_default_row()
        self.parent = parent

        self.setStyleSheet("""
            height: 60px;
            color: #424874;
            border-color: #424874;
            border: 1px solid #424874
        """)

        self.verticalHeader().setDefaultSectionSize(30)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        self.setHorizontalHeader(RiskDataTableHorizontalHeaderView(self))
        self.setHorizontalHeaderLabels(self._column_names)

        self.setStyleSheet(Styles.METHODS_TABLE)

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.verticalHeader().hide()
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 1000)
        self.setFixedHeight(60)

    def initialize_default_row(self) -> None:
        row = self.rowCount()
        self.insertRow(row)
        dummy = QTableWidgetItem()
        self.setItem(row, 0, dummy)
        for col in range(1, len(self._column_names)):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.setItem(row, col, item)
        self.update_height()

    def on_remove_method_clicked(self) -> None:
        button = self.sender()
        if button:
            for row in range(self.rowCount()):
                if self.cellWidget(row, 0) == button:
                    method = self.item(row, 1).text()
                    if method in self.risk_map.methods:
                        self.risk_map.methods.remove(method)
                    self.removeRow(row)
                    break
        self.update_height()
        self.risk_map.mark_modified()

    def update_height(self) -> None:
        row_height = self.rowHeight(0) if self.rowCount() > 0 else 30
        total_height = (self.rowCount() * row_height) + self.horizontalHeader().height() + 2
        self.setFixedHeight(total_height)


class RiskAnalysisMainForm(QWidget):
    def __init__(self, app: QApplication, risk_map: RiskMapFile, parent=None) -> None:
        super().__init__(parent)
        self._app = app
        self.risk_map = risk_map
        self.setStyleSheet(Styles.SCROLL_AREA)

        self._init_scroll_area()
        self._init_title_section()
        self._init_params_section()
        self._init_tables()
        self._init_summary_section()
        self._init_buttons()
        self._assemble_layout()
        self._setup_line_edit_connections()

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


    def _init_title_section(self) -> None:
        self._title_frame = QFrame(self._content_widget)
        self._title_frame.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #424874;
            }
            QLineEdit {
                font-size: 24px;
                font-weight: bold;
                color: #424874;
                background-color: #F4EEFF;
                border: 0;
                border-bottom: 2px solid #424874;
                border-radius: 0;
            }
        """)

        layout = QHBoxLayout(self._title_frame)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        self._mapNoTextEdit = QLineEdit('', self._title_frame)
        self._mapNoTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mapNoTextEdit.setFixedSize(100, 30)

        layout.addStretch()
        layout.addWidget(QLabel('Карта оценки риска №', self._title_frame), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._mapNoTextEdit, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

    def _init_params_section(self) -> None:
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
            ("_professionTextEdit", "Наименование профессии (должности) работника"),
            ("_structureDivisionTextEdit", "Наименование структурного подразделения"),
            ("_workDescriptionTextEdit", "Краткое описание выполняемой работы"),
            ("_usedInstrumentsMaterialsTextEdit", "Используемое оборудование, материалы, сырья"),
            ("_chairmanFullNameTextEdit", "ФИО председателя комиссии по оценке рисков"),
        ]

        for attr_name, label_text in fields:
            edit = QLineEdit('', inner_frame)
            edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            setattr(self, attr_name, edit)

            inner_layout.addWidget(edit)
            inner_layout.addWidget(QLabel(label_text, inner_frame),alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._params_outer_frame = QFrame(self._content_widget)
        outer_layout = QHBoxLayout(self._params_outer_frame)
        outer_layout.addStretch(1)
        outer_layout.addWidget(inner_frame, 2)
        outer_layout.addStretch(1)

    def _init_tables(self) -> None:
        self.risk_data_table_widget = RiskDataTable(app=self._app, parent=self, risk_map=self.risk_map)
        self.methods_data_table_widget = MethodsTable(app=self._app, parent=self, risk_map=self.risk_map)

    def _init_summary_section(self) -> None:
        self._summary_widget = QWidget(self._content_widget)
        self._summary_widget.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #424874;
            }
            QLabel#CLASSIFICATION_VALUE_LOW {
                color: green;
            }
            QLabel#CLASSIFICATION_VALUE_MID {
                color: #fcba03;
            }
            QLabel#CLASSIFICATION_VALUE_HIGH {
                color: red;
            }
        """)

        outer_layout = QHBoxLayout(self._summary_widget)
        outer_layout.setSpacing(0)
        outer_layout.addStretch(1)

        grid = QGridLayout()
        grid.setVerticalSpacing(5)
        grid.setHorizontalSpacing(20)
        outer_layout.addLayout(grid)
        outer_layout.addStretch(1)

        self._summary_risk_level_value_label = QLabel('', parent=self._summary_widget)
        grid.addWidget(QLabel('Уровень профессионального риска на рабочем месте по результатам оценки:', parent=self._summary_widget), 0, 0)
        grid.addWidget(self._summary_risk_level_value_label, 0, 1)

        self._summary_risk_indicator_value = QLineEdit(parent=self._summary_widget)
        self._summary_risk_indicator_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._summary_risk_indicator_value.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #424874;
            border: 0;
            border-bottom: 2px solid #424874;
            border-radius: 0;
        """)

        self._summary_risk_indicator_value.setFixedSize(40, 20)
        grid.addWidget(QLabel('Показатель, учитывающий результаты специальной оценки условий труда:', parent=self._summary_widget), 1, 0)
        grid.addWidget(self._summary_risk_indicator_value, 1, 1)

        self._summary_risk_final_level_value_label = QLabel('', parent=self._summary_widget)
        grid.addWidget(QLabel('Итоговый уровень профессионального риска по результатам оценки:', parent=self._summary_widget), 2, 0)
        grid.addWidget(self._summary_risk_final_level_value_label, 2, 1)

        self._summary_risk_classification_value_label = QLabel('', parent=self._summary_widget)
        grid.addWidget(QLabel('По степени риска рабочее место отнесено к категории:', parent=self._summary_widget), 3, 0)
        grid.addWidget(self._summary_risk_classification_value_label, 3, 1)


    def _init_buttons(self) -> None:
        self._buttons_widget = QWidget()
        self._buttons_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._buttons_widget.setStyleSheet("""
            QPushButton {
                background-color: #A6B1E1;
                border-radius: 20px;
                color: #F4EEFF;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#CalculateButton {
                background-color: #383e92;
            }
            QPushButton#CalculateButton:hover {
                background-color: #241d50;
            }
            QPushButton#ConvertButton {
                background-color: #A6B1E1;
            }
            QPushButton#ConvertButton:hover {
                background-color: #8a9cf3;
            }
        """)

        self.button_calculate = PulsingButton('Рассчитать', parent=self._buttons_widget)
        self.button_calculate.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_calculate.setObjectName('CalculateButton')

        self.button_convert_to = QPushButton('Преобразовать', parent=self._buttons_widget)
        self.button_convert_to.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_convert_to.setObjectName('ConvertButton')

        layout = QHBoxLayout(self._buttons_widget)
        layout.setSpacing(50)
        layout.addStretch()
        layout.addWidget(self.button_calculate)
        layout.addWidget(self.button_convert_to)
        layout.addStretch()


    def _assemble_layout(self) -> None:
        dividers = [self._create_divider() for _ in range(3)]

        content_layout = QVBoxLayout(self._content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        content_layout.addWidget(self._title_frame)
        content_layout.addWidget(dividers[0])
        content_layout.addWidget(self._params_outer_frame)
        content_layout.addWidget(dividers[1])
        content_layout.addWidget(self.risk_data_table_widget)
        content_layout.addWidget(dividers[2])
        content_layout.addWidget(self._summary_widget)
        content_layout.addWidget(self.methods_data_table_widget)

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
            self._mapNoTextEdit: "map_no",
            self._professionTextEdit: "profession",
            self._structureDivisionTextEdit: "department",
            self._workDescriptionTextEdit: "description",
            self._usedInstrumentsMaterialsTextEdit: "tools_and_materials",
            self._chairmanFullNameTextEdit: "chairman",
        }

        for edit, attr in field_map.items():
            edit.textChanged.connect(self._make_field_handler(attr))

        self._summary_risk_indicator_value.textChanged.connect(self._on_risk_indicator_changed)

    def _make_field_handler(self, model_attr: str):
        def handler(text: str):
            if self.risk_map: setattr(self.risk_map, model_attr, text)
        return handler

    def _on_risk_indicator_changed(self, text: str):
        if self.risk_map:
            try: self.risk_map.k_factor = float(text) if text else None
            except ValueError: pass

    def setQLineBlockSignals(self, flag: bool):
        edits = [
            self._mapNoTextEdit,
            self._professionTextEdit,
            self._structureDivisionTextEdit,
            self._workDescriptionTextEdit,
            self._usedInstrumentsMaterialsTextEdit,
            self._chairmanFullNameTextEdit,
            self._summary_risk_indicator_value,
        ]
        for edit in edits: edit.blockSignals(flag)

    @property
    def mapNo_text(self) -> str:
        return self._mapNoTextEdit.text()

    @mapNo_text.setter
    def mapNo_text(self, value: str) -> None:
        self._mapNoTextEdit.setText(value)

    @property
    def profession_text(self) -> str:
        return self._professionTextEdit.text()

    @profession_text.setter
    def profession_text(self, value: str) -> None:
        self._professionTextEdit.setText(value)

    @property
    def structure_division_text(self) -> str:
        return self._structureDivisionTextEdit.text()

    @structure_division_text.setter
    def structure_division_text(self, value: str) -> None:
        self._structureDivisionTextEdit.setText(value)

    @property
    def work_description_text(self) -> str:
        return self._workDescriptionTextEdit.text()

    @work_description_text.setter
    def work_description_text(self, value: str) -> None:
        self._workDescriptionTextEdit.setText(value)

    @property
    def used_materials_text(self) -> str:
        return self._usedInstrumentsMaterialsTextEdit.text()

    @used_materials_text.setter
    def used_materials_text(self, value: str) -> None:
        self._usedInstrumentsMaterialsTextEdit.setText(value)

    @property
    def chairman_fullname_text(self) -> str:
        return self._chairmanFullNameTextEdit.text()

    @chairman_fullname_text.setter
    def chairman_fullname_text(self, value: str)-> None:
        self._chairmanFullNameTextEdit.setText(value)

    @property
    def summary_risk_level_text(self) -> str:
        return self._summary_risk_level_value_label.text()

    @summary_risk_level_text.setter
    def summary_risk_level_text(self, value: str) -> None:
        self._summary_risk_level_value_label.setText(value)

    @property
    def summary_risk_indicator_text(self) -> str:
        return self._summary_risk_indicator_value.text()

    @summary_risk_indicator_text.setter
    def summary_risk_indicator_text(self, value: str) -> None:
        self._summary_risk_indicator_value.setText(value)

    @property
    def summary_risk_final_level_text(self) -> str:
        return self._summary_risk_final_level_value_label.text()

    @summary_risk_final_level_text.setter
    def summary_risk_final_level_text(self, value: str) -> None:
        self._summary_risk_final_level_value_label.setText(value)

    @property
    def summary_risk_classification_text(self)  -> str:
        return self._summary_risk_classification_value_label.text()

    @summary_risk_classification_text.setter
    def summary_risk_classification_text(self, value: str) -> None:
        self._summary_risk_classification_value_label.setText(value)

        classification_map = {
            "Высокий": "CLASSIFICATION_VALUE_HIGH",
            "Средний": "CLASSIFICATION_VALUE_MID",
        }
        object_name = classification_map.get(
            value, "CLASSIFICATION_VALUE_LOW"
        )
        self._summary_risk_classification_value_label.setObjectName(
            object_name
        )

        style = self._summary_risk_classification_value_label.style()
        style.unpolish(self._summary_risk_classification_value_label)
        style.polish(self._summary_risk_classification_value_label)