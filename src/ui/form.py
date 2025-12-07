from PySide6.QtWidgets import (
    QGridLayout, QHeaderView, QLineEdit, QPushButton, QScrollArea, QSizePolicy,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QTableWidget, QStyledItemDelegate, QComboBox,
    QCompleter)
from PySide6.QtCore import Qt
from src.backend.riskMap import RiskMap
import src.backend.database as database
from src.backend.database import database as db


class RiskDataTableHorizontalHeaderView(QHeaderView):
    def __init__(self, parent: QWidget):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.geometriesChanged.connect(self._on_geometries_changed)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        self.setMinimumSize(400, 300)

    def _on_geometries_changed(self):
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
    def __init__(self, parent: QWidget, riskMap: RiskMap):
        self._column_names = [
            '',
            '№ п/п',
            'Опасность',
            'Опасное событие',
            'Качественное значение тяжести ущерба',
            'Качественное значение подверженности опасности',
            'Качественное значение вероятности возникновения опасности',
            'Оценка значимости риска по отдельной опасности',
        ]
        super().__init__(1, len(self._column_names), parent)
        self.riskMap = riskMap
        self._setupUI()
        self._setup_connections()

        self.setItemDelegateForColumn(2, self.ComboBoxDelegate(self))
        self.setItemDelegateForColumn(3, self.ComboBoxDelegate(self))
        self.setItemDelegateForColumn(4, self.ComboBoxDelegate(self))
        self.setItemDelegateForColumn(5, self.ComboBoxDelegate(self))
        self.setItemDelegateForColumn(6, self.ComboBoxDelegate(self))
        self.setItemDelegateForColumn(7, self.ReadOnlyDelegate(self))

        self._initialize_default_row()

    def _setupUI(self):
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
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #4a4a7d;
                background-color: #F4EEFF;
                border: 1px solid #4a4a7d;
            }
            QTableWidget::item {
                height: 40;
                color: #424874;
                font-size: 14px;
                font-weight: bold;
                text-align: center;
                border-left: 1px solid #4a4a7d;
            }
            QHeaderView::section {
                height: 30;
                background-color: #F4EEFF;
                color: #4a4a7d;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                border: 1px solid #4a4a7d;
            }
            QLineEdit {
                background-color: #F4EEFF;
                color: #424874;
                font-size: 14px;
            }
            QPushButton#ManageRowButtonAdd {
                background-color: #F4EEFF; /* Header background */
                color: #4a4a7d; /* Header text color */
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                border: 2px solid #4a4a7d;
                border-radius: 5px;
                margin: 3px 3px 3px 3px;
            }
            QPushButton#ManageRowButtonDelete {
                background-color: #F4EEFF; /* Header background */
                color: #A6B1E1;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                border: 2px solid #A6B1E1;
                border-radius: 5px;
                margin: 3px 3px 3px 3px;
            }
            QPushButton#ManageRowButtonAdd:hover {
                background-color: #a6b1e1;
            }
            QPushButton#ManageRowButtonDelete:hover {
                background-color: #a6b1e1;
                color: #4a4a7d;
                border: 2px solid #4a4a7d;
            }
        """)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)

        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 65)
        self.setColumnWidth(2, 450)
        self.setColumnWidth(3, 450)
        self.setColumnWidth(4, 200)
        self.setColumnWidth(5, 190)
        self.setColumnWidth(6, 200)
        self.setColumnWidth(7, 230)
        self.setFixedHeight(100)

    class ReadOnlyDelegate(QStyledItemDelegate):
        def createEditor(self, parent, option, index):
            return None

    class ComboBoxDelegate(QStyledItemDelegate):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent_table = parent

        def createEditor(self, parent, option, index):
            editor = QComboBox(parent)
            editor.setEditable(True)
            editor.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            editor.completer().setCompletionMode(QCompleter.PopupCompletion)
            editor.completer().setFilterMode(Qt.MatchFlag.MatchContains)

            editor.setStyleSheet("""
                        QComboBox {
                            background-color: #F4EEFF;
                            color: #424874;
                            font-size: 14px;
                            text-align: left;
                            border: 1px solid #4a4a7d;
                        }
                        QComboBox QAbstractItemView {
                            background-color: #F4EEFF;
                            color: #424874;
                            selection-background-color:#a6b1e1;
                            selection-color: #4a4a7d;
                        }
                    """)

            if index.column() == 2:
                editor.addItems(db.getDangers())
            elif index.column() == 3:
                danger_item = self.parent_table.item(index.row(), 2).text()
                editor.addItems(db.getEvents(danger_item))
            elif index.column() == 4:
                editor.addItems(list(database.DAMAGE.keys()))
            elif index.column() == 5:
                editor.addItems(list(database.SUSCEPTIBILITY.keys()))
            elif index.column() == 6:
                editor.addItems(list(database.PROBABILITY.keys()))
            return editor

        def setEditorData(self, editor, index):
            value = index.model().data(index, Qt.DisplayRole)
            if value:
                editor.setCurrentText(value)

        def setModelData(self, editor, model, index):
            value = editor.currentText()
            model.setData(index, value, Qt.ItemDataRole.EditRole)

        def updateEditorGeometry(self, editor, option, index):
            editor.setGeometry(option.rect)

    def _setup_connections(self):
        self.cellChanged.connect(self._onCellChanged)

    def _onCellChanged(self,  row, column):
        if row == self.rowCount() - 1:
            return
        if column == 2:
            self._updateDanger(row)
        elif column == 3:
            self._updateEvent(row)
        elif column in (4, 5, 6):
            self._updateRiskParams(row)

    def _updateDanger(self, row: int):
        dangerItem = self.item(row, 2)
        if not dangerItem:
            return
        danger = dangerItem.text()
        if danger in db.getDangers():
            self.item(row, 2).setText(danger)
            self.setItem(row, 3, QTableWidgetItem(""))
            self.setItem(row, 4, QTableWidgetItem(""))
            self.setItem(row, 5, QTableWidgetItem(""))
            self.setItem(row, 6, QTableWidgetItem(""))
            record = self._getOrCreateRecord(row)
            record.danger = danger
        else:
            self.item(row, 2).setText("")
            self.setItem(row, 3, QTableWidgetItem(""))
            self.setItem(row, 4, QTableWidgetItem(""))
            self.setItem(row, 5, QTableWidgetItem(""))
            self.setItem(row, 6, QTableWidgetItem(""))
        self.riskMap._isModified = True

    def _updateEvent(self, row):
        event_item = self.item(row, 3)
        danger_item = self.item(row, 2)
        if not event_item or not danger_item:
            return
        event = event_item.text()
        danger = danger_item.text()
        if danger in db.getDangers() and event in db.getEvents(danger):
            record = self._getOrCreateRecord(row)
            record.event = event
        else:
            self.setItem(row, 4, QTableWidgetItem(""))
            self.setItem(row, 5, QTableWidgetItem(""))
            self.setItem(row, 6, QTableWidgetItem(""))
        self.riskMap._isModified = True

    def _updateRiskParams(self, row):
        for col in range(4, 7):
            if not self.item(row, col) or not self.item(row, col).text():
                return

        record = self._getOrCreateRecord(row)
        damage = self.item(row, 4).text()
        if damage in list(database.DAMAGE.keys()):
           record.damage = damage

        susceptibility = self.item(row, 5).text()
        if susceptibility in list(database.SUSCEPTIBILITY.keys()):
            record.susceptibility = susceptibility

        probability = self.item(row, 6).text()
        if probability in list(database.PROBABILITY.keys()):
            record.probability = probability
        self.riskMap._isModified = True

    def _getOrCreateRecord(self, row):
        if row >= len(self.riskMap.table):
            self.riskMap.tableAddRecord()
        return self.riskMap.table[row]

    # Инициализация строки с кнопкой добавления дополнительных строк
    def _initialize_default_row(self):
        row = self.rowCount()
        self.insertRow(row)

        add_button = QPushButton('+')
        add_button.setObjectName('ManageRowButtonAdd')
        add_button.clicked.connect(self.add_row)
        self.setCellWidget(row, 0, add_button)

        for col in range(1, len(self._column_names)):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if col == 1 or col == 7:
                item.setFlags(Qt.ItemFlag.NoItemFlags)
            else:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.setItem(row, col, item)

        self.update_custom_numbering()
        self.updateHeight()

    # Добавление строки в таблицу
    def add_row(self):
        row_index = self.rowCount() - 1
        self.insertRow(row_index)
        self.riskMap.tableAddRecord()

        remove_button = QPushButton('-')
        remove_button.setObjectName('ManageRowButtonDelete')
        remove_button.clicked.connect(self.on_remove_row_clicked)
        self.setCellWidget(row_index, 0, remove_button)

        for col in range(1, len(self._column_names)):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setData(Qt.ItemDataRole.UserRole, Qt.TextFlag.TextWordWrap)
            if col == 1 or col == 7:
                item.setFlags(Qt.ItemFlag.NoItemFlags)
            else:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)

            self.setItem(row_index, col, item)

        self.update_custom_numbering()
        self.updateHeight()

    # Удаление строк из таблицы по кнопке
    def on_remove_row_clicked(self):
        button = self.sender()
        if button:
            for row in range(self.rowCount() - 1):
                if self.cellWidget(row, 0) == button:
                    self.removeRow(row)
                    if row < len(self.riskMap.table):
                        self.riskMap.tableRemoveRecord(row)
                    break

        self.update_custom_numbering()
        self.updateHeight()
        self.riskMap._markModified()

    def updateHeight(self):
        rowHeight = self.rowHeight(0) if self.rowCount() > 0 else 30
        totalHeight = (self.rowCount() * rowHeight) + self.horizontalHeader().height() + 2
        self.setFixedHeight(totalHeight)

    # Обновление номеров строк в таблице
    def update_custom_numbering(self):
        for row in range(self.rowCount() - 1):
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.setItem(row, 1, num_item)


class MethodsTable(QTableWidget):
    def __init__(self, parent: QWidget, riskMap: RiskMap):
        self._column_names = [
            '',
            'Общие меры по управлению рисками'
        ]

        super().__init__(1, len(self._column_names), parent)
        self.riskMap = riskMap
        self._initialize_default_row()
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
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #4a4a7d;
                background-color: #F4EEFF;
                border: 1px solid #4a4a7d
            }
            QTableWidget::item {
                height: 40;
                color: #424874;
                font-size: 14px;
                text-align: center;
                border-left: 1px solid #4a4a7d
            }
            QHeaderView::section {
                height: 30;
                background-color: #F4EEFF;
                color: #4a4a7d;
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                border: 1px solid #4a4a7d;
            }
            QPushButton#ManageRowButton {
                background-color: #F4EEFF; /* Header background */
                color: #4a4a7d; /* Header text color */
                font-weight: bold;
                font-size: 14px;
                text-align: center;
                border: 2px solid #4a4a7d;
                border-radius: 5px;
                margin: 3px 3px 3px 3px;
            }
            QPushButton#ManageRowButton:hover {
                background-color: #a6b1e1;
            }
        """)
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

    def _initialize_default_row(self):
        row = self.rowCount()
        self.insertRow(row)
        dummy = QTableWidgetItem()
        self.setItem(row, 0, dummy)
        for col  in range(1, len(self._column_names)):
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.setItem(row, col, item)
        self.updateHeight()

    def _onRemoveMethodClicked(self):
        button = self.sender()
        if button:
            for row in range(self.rowCount()):
                if self.cellWidget(row, 0) == button:
                    method = self.item(row, 1).text()
                    if method in self.riskMap.methods:
                        self.riskMap.methods.remove(method)
                    self.removeRow(row)
                    break
        self.updateHeight()
        self.riskMap._markModified()

    def updateHeight(self):
        row_height = self.rowHeight(0) if self.rowCount() > 0 else 30
        total_height = (self.rowCount() * row_height) + self.horizontalHeader().height() + 2
        self.setFixedHeight(total_height)


class RiskAnalysisMainForm(QWidget):
    def __init__(self, riskMap: RiskMap, parent=None):
        super().__init__(parent)
        self.riskMap = riskMap
        self.setStyleSheet("""
            QScrollBar:horizontal {
                border: none;
                border-radius: 5px;
                background: #DCD6F7;
                height: 14px;
                margin: 0px 20px 0 20px;
            }
            QScrollBar::handle:horizontal {
                background: #A6B1E1;
                min-width: 20px;
            }
            QScrollBar::add-line:horizontal {
                border: none;
                background: #DCD6F7;
                width: 20px;
                height: 14px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:horizontal {
                border: none;
                background: #DCD6F7;
                width: 20px;
                height: 14px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:horizontal {
                border: none;
                background: #DCD6F7;
                width: 20px;
                height: 14px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }
            QScrollBar:vertical {
                border: none;
                border-radius: 5px;
                background: #DCD6F7;
                width: 14px;
                margin: 20px 0 20px 0;
            }
            QScrollBar::handle:vertical {
                background: #A6B1E1;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical {
                border: none;
                background: #DCD6F7;
                height: 20px;
                width: 14px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }
            QScrollBar::sub-line:vertical {
                border: none;
                background: #DCD6F7;
                height: 20px;
                width: 14px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: #F4EEFF;
            }
        """)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_scroll_widget = QWidget()
        main_scroll_widget.setStyleSheet("""
            background-color: #F4EEFF
        """)

        table_widget = QWidget(main_scroll_widget)
        table_widget.setStyleSheet("""
            background-color: #F4EEFF
        """)

        table_widget_title_frame = QFrame(table_widget)
        table_widget_title_frame.setStyleSheet("""
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

        table_widget_title_layout = QHBoxLayout(table_widget_title_frame)
        table_widget_title_layout.setSpacing(10)
        table_widget_title_layout.setContentsMargins(0, 0, 0, 0)

        self._mapNoTextEdit = QLineEdit('', table_widget_title_frame)
        self._mapNoTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mapNoTextEdit.setFixedSize(100, 30)
        table_widget_title_layout.addStretch()
        table_widget_title_layout.addWidget(QLabel('Карта оценки риска №', table_widget_title_frame), alignment=Qt.AlignmentFlag.AlignCenter)
        table_widget_title_layout.addWidget(self._mapNoTextEdit, alignment=Qt.AlignmentFlag.AlignCenter)
        table_widget_title_layout.addStretch()

        table_widget_divider1 = QFrame(table_widget)
        table_widget_divider1.setFrameShape(QFrame.Shape.HLine)
        table_widget_divider1.setFrameShadow(QFrame.Shadow.Sunken)
        table_widget_divider1.setStyleSheet("border: 4px solid #A6B1E1;")

        table_params_inner_frame = QFrame(table_widget)
        table_params_inner_frame.setStyleSheet("""
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
        table_params_frame_inner_layout = QVBoxLayout(table_params_inner_frame)
        table_params_frame_inner_layout.setSpacing(1)
        table_params_frame_inner_layout.setContentsMargins(20, 20, 20, 20)

        self._professionTextEdit = QLineEdit('', table_params_inner_frame)
        self._professionTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._professionTextEdit)
        table_params_frame_inner_layout.addWidget(
            QLabel('Наименование профессии (должности) работника', table_params_inner_frame),
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._structureDivisionTextEdit = QLineEdit('', table_params_inner_frame)
        self._structureDivisionTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._structureDivisionTextEdit)
        table_params_frame_inner_layout.addWidget(
            QLabel('Наименование структурного подразделения', table_params_inner_frame),
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._workDescriptionTextEdit = QLineEdit('', table_params_inner_frame)
        self._workDescriptionTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._workDescriptionTextEdit)
        table_params_frame_inner_layout.addWidget(
            QLabel('Краткое описание выполняемой работы', table_params_inner_frame),
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._usedInstrumentsMaterialsTextEdit = QLineEdit('', table_params_inner_frame)
        self._usedInstrumentsMaterialsTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._usedInstrumentsMaterialsTextEdit)
        table_params_frame_inner_layout.addWidget(
            QLabel('Используемое оборудование, материалы, сырья', table_params_inner_frame),
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._chairmanFullNameTextEdit = QLineEdit('', table_params_inner_frame)
        self._chairmanFullNameTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._chairmanFullNameTextEdit)
        table_params_frame_inner_layout.addWidget(
            QLabel('ФИО председателя комиссии по оценке рисков', table_params_inner_frame),
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        table_widget_divider2 = QFrame(table_widget)
        table_widget_divider2.setFrameShape(QFrame.Shape.HLine)
        table_widget_divider2.setFrameShadow(QFrame.Shadow.Sunken)
        table_widget_divider2.setStyleSheet("border: 4px solid #A6B1E1;")


        table_widget_divider3 = QFrame(table_widget)
        table_widget_divider3.setFrameShape(QFrame.Shape.HLine)
        table_widget_divider3.setFrameShadow(QFrame.Shadow.Sunken)
        table_widget_divider3.setStyleSheet("border: 4px solid #A6B1E1;")

        table_summary_widget = QWidget(table_widget)
        table_summary_widget.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #424874;
            }
            QLabel#CLASSIFICATION_VALUE_LOW {
                color: green;
            }
            QLabel#CLASSIFICATION_VALUE_MID {
                color: #fcba03
            }
            QLabel#CLASSIFICATION_VALUE_HIGH {
                color: red
            }
        """)
        table_summary_widget_layout_outer = QHBoxLayout(table_summary_widget)
        table_summary_widget_layout_outer.setSpacing(0)
        table_summary_widget_layout_outer.addStretch(1)
        table_summary_widget_layout_inner = QGridLayout()
        table_summary_widget_layout_inner.setVerticalSpacing(5)
        table_summary_widget_layout_inner.setHorizontalSpacing(20)
        table_summary_widget_layout_outer.addLayout(table_summary_widget_layout_inner)
        table_summary_widget_layout_outer.addStretch(1)

        summary_risk_level_description_label = QLabel(parent=table_summary_widget)
        summary_risk_level_description_label.setText(
            'Уровень профессионального риска на рабочем месте по результатам оценки:')
        self._summary_risk_level_value_label = QLabel(f'', parent=table_summary_widget)
        table_summary_widget_layout_inner.addWidget(summary_risk_level_description_label, 0, 0)
        table_summary_widget_layout_inner.addWidget(self._summary_risk_level_value_label, 0, 1)

        summary_risk_indicator_description_label = QLabel(parent=table_summary_widget)
        summary_risk_indicator_description_label.setText(
            'Показатель, учитывающий результаты специальной оценки условий труда:')
        self._summary_risk_indicator_value = QLineEdit(parent=table_summary_widget)
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
        table_summary_widget_layout_inner.addWidget(summary_risk_indicator_description_label, 1, 0)
        table_summary_widget_layout_inner.addWidget(self._summary_risk_indicator_value, 1, 1)

        summary_risk_final_level_description_label = QLabel(parent=table_summary_widget)
        summary_risk_final_level_description_label.setText(
            'Итоговый уровень профессионального риска по результатам оценки:')
        self._summary_risk_final_level_value_label = QLabel(f'', parent=table_summary_widget)
        table_summary_widget_layout_inner.addWidget(summary_risk_final_level_description_label, 2, 0)
        table_summary_widget_layout_inner.addWidget(self._summary_risk_final_level_value_label, 2, 1)

        summary_risk_classification_description_label = QLabel(parent=table_summary_widget)
        summary_risk_classification_description_label.setText('По степени риска рабочее место отнесено к категории:')
        self._summary_risk_classification_value_label = QLabel(f'', parent=table_summary_widget)
        table_summary_widget_layout_inner.addWidget(summary_risk_classification_description_label, 3, 0)
        table_summary_widget_layout_inner.addWidget(self._summary_risk_classification_value_label, 3, 1)

        buttons_widget = QWidget()
        buttons_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        buttons_widget.setStyleSheet("""
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

        self.button_calculate = QPushButton('Расcчитать', parent=buttons_widget)
        self.button_calculate.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_calculate.setObjectName('CalculateButton')
        self.button_convert_to = QPushButton('Преобразовать в doc', parent=buttons_widget)
        self.button_convert_to.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_convert_to.setObjectName('ConvertButton')

        table_params_outer_frame = QFrame(table_widget)
        table_params_outer_layout = QHBoxLayout(table_params_outer_frame)
        table_params_outer_layout.addStretch(1)
        table_params_outer_layout.addWidget(table_params_inner_frame, 2)
        table_params_outer_layout.addStretch(1)

        self.riskDataTableWidget = RiskDataTable(parent=self, riskMap=self.riskMap)
        self.methodsDataTableWidget = MethodsTable(parent=self, riskMap=self.riskMap)

        table_widget_layout = QVBoxLayout(table_widget)
        table_widget_layout.setSpacing(20)
        table_widget_layout.setContentsMargins(20, 20, 20, 20)
        table_widget_layout.addWidget(table_widget_title_frame)
        table_widget_layout.addWidget(table_widget_divider1)
        table_widget_layout.addWidget(table_params_outer_frame)
        table_widget_layout.addWidget(table_widget_divider2)
        table_widget_layout.addWidget(self.riskDataTableWidget)
        table_widget_layout.addWidget(table_widget_divider3)
        table_widget_layout.addWidget(table_summary_widget)
        table_widget_layout.addWidget(self.methodsDataTableWidget)

        buttons_widget_layout = QHBoxLayout(buttons_widget)
        buttons_widget_layout.setSpacing(50)
        buttons_widget_layout.addStretch()
        buttons_widget_layout.addWidget(self.button_calculate)
        buttons_widget_layout.addWidget(self.button_convert_to)
        buttons_widget_layout.addStretch()

        main_scroll_layout = QVBoxLayout(main_scroll_widget)
        main_scroll_layout.addWidget(table_widget)
        main_scroll_layout.addWidget(buttons_widget)

        scroll_area.setWidget(main_scroll_widget)
        self._setup_line_edit_connections()
        self.showMaximized()

    # Свойства, упрощающие менеджмент данных
    # Для получения текста профессии: self.title_table_text, возвращаемое значение - строка
    # Для присвоения значения профессии используем self.title_table_text = значение,
    # строка запишется в виджет и будет видна пользователю

    def _setup_line_edit_connections(self):
        self._mapNoTextEdit.textChanged.connect(self._on_map_no_changed)
        self._professionTextEdit.textChanged.connect(self._on_profession_changed)
        self._structureDivisionTextEdit.textChanged.connect(self._on_structure_division_changed)
        self._workDescriptionTextEdit.textChanged.connect(self._on_work_description_changed)
        self._usedInstrumentsMaterialsTextEdit.textChanged.connect(self._on_used_materials_changed)
        self._chairmanFullNameTextEdit.textChanged.connect(self._on_chairman_changed)
        self._summary_risk_indicator_value.textChanged.connect(self._on_risk_indicator_changed)

    def _on_map_no_changed(self, text):
        if self.riskMap:
            self.riskMap.mapNo = text

    def _on_profession_changed(self, text):
        if self.riskMap:
            self.riskMap.profession = text

    def _on_structure_division_changed(self, text):
        if self.riskMap:
            self.riskMap.structDivision = text

    def _on_work_description_changed(self, text):
        if self.riskMap:
            self.riskMap.description = text

    def _on_used_materials_changed(self, text):
        if self.riskMap:
            self.riskMap.toolsMaterials = text
    def _on_chairman_changed(self, text):
        if self.riskMap:
            self.riskMap.chairman = text

    def _on_risk_indicator_changed(self, text):
        if self.riskMap:
            try:
                self.riskMap.kFactor = float(text) if text else None
            except ValueError:
                pass

    def setQLineBlockSignals(self, flag: bool):
        self._mapNoTextEdit.blockSignals(flag)
        self._professionTextEdit.blockSignals(flag)
        self._structureDivisionTextEdit.blockSignals(flag)
        self._workDescriptionTextEdit.blockSignals(flag)
        self._usedInstrumentsMaterialsTextEdit.blockSignals(flag)
        self._chairmanFullNameTextEdit.blockSignals(flag)
        self._summary_risk_indicator_value.blockSignals(flag)

    @property
    def mapNo_text(self):
        return self._mapNoTextEdit.text()

    @mapNo_text.setter
    def mapNo_text(self, value: str):
        self._mapNoTextEdit.setText(value)

    @property
    def profession_text(self):
        return self._professionTextEdit.text()

    @profession_text.setter
    def profession_text(self, value: str):
        self._professionTextEdit.setText(value)

    @property
    def structure_division_text(self):
        return self._structureDivisionTextEdit.text()

    @structure_division_text.setter
    def structure_division_text(self, value: str):
        self._structureDivisionTextEdit.setText(value)

    @property
    def work_description_text(self):
        return self._workDescriptionTextEdit.text()

    @work_description_text.setter
    def work_description_text(self, value: str):
        self._workDescriptionTextEdit.setText(value)

    @property
    def used_materials_text(self):
        return self._usedInstrumentsMaterialsTextEdit.text()

    @used_materials_text.setter
    def used_materials_text(self, value: str):
        self._usedInstrumentsMaterialsTextEdit.setText(value)

    @property
    def chairman_fullname_text(self):
        return self._chairmanFullNameTextEdit.text()

    @chairman_fullname_text.setter
    def chairman_fullname_text(self, value: str):
        self._chairmanFullNameTextEdit.setText(value)

    @property
    def summary_risk_level_text(self):
        return self._summary_risk_level_value_label.text()

    @summary_risk_level_text.setter
    def summary_risk_level_text(self, value: str):
        self._summary_risk_level_value_label.setText(value)

    @property
    def summary_risk_indicator_text(self):
        return self._summary_risk_indicator_value.text()

    @summary_risk_indicator_text.setter
    def summary_risk_indicator_text(self, value: str):
        self._summary_risk_indicator_value.setText(value)

    @property
    def summary_risk_final_level_text(self):
        return self._summary_risk_final_level_value_label.text()

    @summary_risk_final_level_text.setter
    def summary_risk_final_level_text(self, value: str):
        self._summary_risk_final_level_value_label.setText(value)

    @property
    def summary_risk_classification_text(self):
        return self._summary_risk_classification_value_label.text()

    @summary_risk_classification_text.setter
    def summary_risk_classification_text(self, value: str):
        self._summary_risk_classification_value_label.setText(value)

    @summary_risk_classification_text.setter
    def summary_risk_classification_text(self, value: str):
        self._summary_risk_classification_value_label.setText(value)

        if value == "Высокий":
            self._summary_risk_classification_value_label.setObjectName('CLASSIFICATION_VALUE_HIGH')
        elif value == "Средний":
            self._summary_risk_classification_value_label.setObjectName('CLASSIFICATION_VALUE_MID')
        else:
            self._summary_risk_classification_value_label.setObjectName('CLASSIFICATION_VALUE_LOW')

        self._summary_risk_classification_value_label.style().unpolish(self._summary_risk_classification_value_label)
        self._summary_risk_classification_value_label.style().polish(self._summary_risk_classification_value_label)
