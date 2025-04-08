from .form import RiskAnalysisMainForm


# Главный класс программы, если требуются подробности см. содержимое файла form.py
class RiskAnalysisMainWindow(RiskAnalysisMainForm):
    def __init__(self):
        super().__init__()
        self.button_calculate.clicked.connect(self.on_calc_button_clicked)
        self.button_convert_to.clicked.connect(self.on_convert_button_clicked)

        # Переменная таблицы, для получения данных потребуется использовать индексы, для
        # ручного добавления/удаления строк использовать методы self.add_row, self.remove_row (см. файл form.py)
        # Для управления данными таблицы, требуется изучить класс QTableWidget из Qt
        # self.riskDataTableWidget

    # Обратный вызов для кнопки Calc
    def on_calc_button_clicked(self):
        print('CALC!')

    # Обратный вызов для кнопки Convert to
    def on_convert_button_clicked(self):
        print('CONVERT!')
