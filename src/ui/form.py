from PySide6.QtWidgets import (
    QHeaderView, QLineEdit, QMainWindow, QMenu, QPushButton, QScrollArea, QSizePolicy, QTableWidgetItem, QVBoxLayout, 
    QHBoxLayout, QWidget, QLabel, QFrame, QTableWidget
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt


class RiskDataTableHorizontalHeaderView(QHeaderView):
    def __init__(self, parent: QWidget):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.geometriesChanged.connect(self._on_geometries_changed)
        self.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        # self.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

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
    def __init__(self, parent: QWidget):
        self._column_names = [
            '✏️',
            '№',
            'List №',
            'Risk',
            'Event',
            'Qual. value of severity',
            'Pts. value of severity',
            'Qual. value of hazard exposure',
            'Pts. value of hazard exposure',
            'Qual. value of hazard occurrence',
            'Pts. value of hazard occurrence',
            'Sum of weighing factors',
            'Weighting coefficient of probability of danger  occurrence',
            'Risks for identified hazards',
            'Risk significance assessment for a particular hazard',
        ]

        super().__init__(1, len(self._column_names), parent)
        
        self.setStyleSheet("""
            color: #424874;
            border-color: #424874;
        """)
        self.setHorizontalHeader(RiskDataTableHorizontalHeaderView(self))
        self.setHorizontalHeaderLabels(self._column_names)
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #4a4a7d; /* Grid color */
                background-color: #e6e6fa; /* Background color */
            }
            QTableWidget::item {
                padding: 10px;
                color: black;
            }
            QHeaderView::section {
                background-color: #e6e6fa; /* Header background */
                color: #4a4a7d; /* Header text color */
                font-weight: bold;
                text-align: center;
                border: 1px solid #4a4a7d;
            }
            QPushButton#ManageRowButton {
                background-color: #e6e6fa; /* Header background */
                color: #4a4a7d; /* Header text color */
                font-weight: bold;
                text-align: center;
            }
        """)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self._initialize_default_row()
    
    # Инициализация строки с кнопкой добавления дополнительных строк
    def _initialize_default_row(self):
        add_button = QPushButton('+')
        add_button.setObjectName('ManageRowButton')
        add_button.clicked.connect(self.add_row)
        self.setCellWidget(0, 0, add_button)

        for col in range(1, len(self._column_names)):
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.setItem(0, col, item)

        self.update_custom_numbering()
    
    # Добавление строки в таблицу
    def add_row(self):
        row_index = self.rowCount() - 1
        self.insertRow(row_index)

        remove_button = QPushButton('-')
        remove_button.setObjectName('ManageRowButton')
        remove_button.clicked.connect(self.on_remove_row_clicked)
        self.setCellWidget(row_index, 0, remove_button)

        for col in range(1, len(self._column_names)):
            item = QTableWidgetItem()
            if col == 2:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            else:
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)
            self.setItem(0, col, item)

        self.update_custom_numbering()
    
    # Удаление строк из таблицы по кнопке
    def on_remove_row_clicked(self):
        button = self.sender()
        
        removed = False

        if button:
            for row in range(self.rowCount() - 1):
                if self.cellWidget(row, 0) == button:
                    self.removeRow(row)
                    removed = True
                    break
        
        if removed:
            self.update_custom_numbering()
    
    # Обновление номеров строк в таблице
    def update_custom_numbering(self):
        for row in range(self.rowCount() - 1):
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            num_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.setItem(row, 1, num_item)


class RiskAnalysisMainForm(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Risk Analysis App")
        self.setGeometry(200, 200, 400, 300)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #e6e6fa;
            }
            QScrollBar:horizontal {
                border: none;
                background: #DCD6F7;
                height: 12px;
                margin: 0px 20px 0 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background: #A6B1E1;
                min-width: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
            }
            QScrollBar:vertical {
                border: none;
                background: #DCD6F7;
                width: 12px;
                margin: 20px 0 20px 0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #A6B1E1;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
            QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                border: none;
                background: none;
                color: none;
                width: 0px;
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background-color: #DCD6F7;
            }
        """)

        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #4a4a7d;
                color: white;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3b3b68;
            }
        """)

        self._top_dropdown_menu = QMenu("☰ Menu", menu_bar)
        self._top_dropdown_menu.setStyleSheet("""
            QMenu {
                background-color: #4a4a7d;
                color: white;
                border: 1px solid #3b3b68;
            }
            QMenu::item {
                padding: 5px 15px;
                border: none;
            }
            QMenu::item:selected {
                background-color: #3b3b68;
            }
        """)

        for i in range(1, 6):
            action = QAction(f"Option {i}", self._top_dropdown_menu)
            action.setIcon(QIcon.fromTheme("folder"))
            self._top_dropdown_menu.addAction(action)

        menu_bar.addMenu(self._top_dropdown_menu)

        table_widget = QWidget(self)
        table_widget.setStyleSheet("""
            background-color: #F4EEFF
        """)

        table_widget_scrollarea = QScrollArea()
        table_widget_scrollarea.setWidgetResizable(True)
        table_widget_scrollarea.setWidget(table_widget)
        
        self._title_label = QLabel("Table 1", table_widget)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setStyleSheet("font-size: 24px; color: #4a4a7d; font-weight: bold;")

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
                font-size: 14px;
                color: #424874;
                background-color: #E9E4FF;
                border: 0;
                border-bottom: 2px solid #424874;
                border-radius: 0;
            }
        """)
        table_params_frame_inner_layout = QVBoxLayout(table_params_inner_frame)
        table_params_frame_inner_layout.setSpacing(5)
        table_params_frame_inner_layout.setContentsMargins(20, 20, 20, 20)
        
        self._professionTextEdit = QLineEdit('', table_params_inner_frame)
        self._professionTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._professionTextEdit)
        table_params_frame_inner_layout.addWidget(QLabel('Profession', table_params_inner_frame),
                                                  alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._structureDivisionTextEdit = QLineEdit('', table_params_inner_frame)
        self._structureDivisionTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._structureDivisionTextEdit)
        table_params_frame_inner_layout.addWidget(QLabel('Structure division', table_params_inner_frame),
                                                  alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._workDescriptionTextEdit = QLineEdit('', table_params_inner_frame)
        self._workDescriptionTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._workDescriptionTextEdit)
        table_params_frame_inner_layout.addWidget(QLabel('Brief description of work', table_params_inner_frame),
                                                  alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self._usedInstrumentsMaterialsTextEdit = QLineEdit('', table_params_inner_frame)
        self._usedInstrumentsMaterialsTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self._usedInstrumentsMaterialsTextEdit)
        table_params_frame_inner_layout.addWidget(QLabel('Used instruments and materials', table_params_inner_frame),
                                                  alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.regulatoryDocumentsTextEdit = QLineEdit('', table_params_inner_frame)
        self.regulatoryDocumentsTextEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_params_frame_inner_layout.addWidget(self.regulatoryDocumentsTextEdit)
        table_params_frame_inner_layout.addWidget(QLabel('Regulatory documents', table_params_inner_frame),
                                                  alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        table_widget_divider2 = QFrame(table_widget)
        table_widget_divider2.setFrameShape(QFrame.Shape.HLine)
        table_widget_divider2.setFrameShadow(QFrame.Shadow.Sunken)
        table_widget_divider2.setStyleSheet("border: 4px solid #A6B1E1;")

        self.riskDataTableWidget = RiskDataTable(table_widget)

        table_widget_divider3 = QFrame(table_widget)
        table_widget_divider3.setFrameShape(QFrame.Shape.HLine)
        table_widget_divider3.setFrameShadow(QFrame.Shadow.Sunken)
        table_widget_divider3.setStyleSheet("border: 4px solid #A6B1E1;")

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
            QPushButton#Calculate {
                background-color: #424874; 
            }
            QPushButton:hover {
                background-color: #8a9cf3;
            }
            QPushButton#Calculate:hover {
                background-color: #3c3c6c;
            }
        """)
        
        self.button_print = QPushButton('Print', parent=buttons_widget)
        self.button_print.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_calculate = QPushButton('Calculate', parent=buttons_widget)
        self.button_calculate.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.button_calculate.setObjectName('Calculate')
        self.button_convert_to = QPushButton('Convert to...', parent=buttons_widget)
        self.button_convert_to.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        table_params_outer_frame = QFrame(table_widget)
        table_params_outer_layout = QHBoxLayout(table_params_outer_frame)
        table_params_outer_layout.addStretch(1)
        table_params_outer_layout.addWidget(table_params_inner_frame, 2)
        table_params_outer_layout.addStretch(1)

        table_widget_layout = QVBoxLayout(table_widget)
        table_widget_layout.setSpacing(20)
        table_widget_layout.setContentsMargins(20, 20, 20, 20)
        table_widget_layout.addWidget(self._title_label)
        table_widget_layout.addWidget(table_widget_divider1)
        table_widget_layout.addWidget(table_params_outer_frame)
        table_widget_layout.addWidget(table_widget_divider2)
        table_widget_layout.addWidget(self.riskDataTableWidget)
        table_widget_layout.addWidget(table_widget_divider3)

        buttons_widget_layout = QHBoxLayout(buttons_widget)
        buttons_widget_layout.setSpacing(50)
        buttons_widget_layout.addStretch()
        buttons_widget_layout.addWidget(self.button_print)
        buttons_widget_layout.addWidget(self.button_calculate)
        buttons_widget_layout.addWidget(self.button_convert_to)
        buttons_widget_layout.addStretch()

        main_widget = QWidget()
        main_widget_layout = QVBoxLayout(main_widget)
        main_widget_layout.setContentsMargins(25, 25, 25, 25)
        main_widget_layout.addWidget(table_widget)
        main_widget_layout.addWidget(buttons_widget)

        self.setLayout(main_widget_layout)
        self.setCentralWidget(main_widget)
    
    # Свойства, упрощающие менеджмент данных
    # Для получения текста профессии: self.title_table_text, возвращаемое значение - строка
    # Для присвоения значения профессии используем self.title_table_text = значение,
    # строка запишется в виджет и будет видна пользователю

    @property
    def title_table_text(self):
        return self._title_label.text()

    @title_table_text.setter
    def title_table_text(self, value: str):
        self._title_label.setText(value)

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

