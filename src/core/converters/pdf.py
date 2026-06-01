from src.core.converters.base import Converter
from src.models.risk_map import RiskMapFile

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
from PySide6.QtWidgets import QApplication


class RiskMapToPdfConverter(Converter[RiskMapFile]):
    FILTER_STRING = "Документы PDF (*.pdf)"
    OUTPUT_FORMAT = "pdf"

    def __init__(self, app: QApplication, risk_map: RiskMapFile):
        super().__init__(app, risk_map)
        self._file: RiskMapFile = risk_map
        self._story = []
        self._setup_fonts()
        self._styles = self._create_styles()

    def convert(self, output_path: Path | str) -> None:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
            title=f"Карта оценки риска №{self._file.map_no if self._file.map_no else ''}",
            author=self._METADATA.get("author", ""),
            subject=self._METADATA.get("comments", "")
        )

        self._add_logo()
        self._add_approval_section()
        self._add_title()
        self._add_main_info()
        self._add_summary_table()
        self._add_risk_table()
        self._add_methods()

        doc.build(self._story)

    @staticmethod
    def _setup_fonts() -> None:
        try:
            pdfmetrics.registerFont(TTFont('TimesNewRoman', 'times.ttf'))
            pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', 'timesbd.ttf'))
        except Exception:
            pass

    @staticmethod
    def _create_styles() -> dict:
        styles = getSampleStyleSheet()

        try:
            font_name = 'TimesNewRoman'
            font_name_bold = 'TimesNewRoman-Bold'
        except Exception:
            font_name = 'Times-Roman'
            font_name_bold = 'Times-Bold'

        custom_styles = {
            'Normal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=10,
                leading=12
            ),
            'Bold': ParagraphStyle(
                'CustomBold',
                parent=styles['Normal'],
                fontName=font_name_bold,
                fontSize=10,
                leading=12
            ),
            'Center': ParagraphStyle(
                'CustomCenter',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=10,
                alignment=TA_CENTER
            ),
            'CenterBold': ParagraphStyle(
                'CustomCenterBold',
                parent=styles['Normal'],
                fontName=font_name_bold,
                fontSize=10,
                alignment=TA_CENTER
            ),
            'Small': ParagraphStyle(
                'CustomSmall',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=8,
                leading=10
            ),
            'SmallBold': ParagraphStyle(
                'CustomSmallBold',
                parent=styles['Normal'],
                fontName=font_name_bold,
                fontSize=8,
                leading=10
            ),
            'SmallCenter': ParagraphStyle(
                'CustomSmallCenter',
                parent=styles['Normal'],
                fontName=font_name,
                fontSize=8,
                alignment=TA_CENTER
            ),
            'SmallCenterBold': ParagraphStyle(
                'CustomSmallCenterBold',
                parent=styles['Normal'],
                fontName=font_name_bold,
                fontSize=8,
                alignment=TA_CENTER
            )
        }

        return custom_styles

    def _add_logo(self) -> None:
        try:
            logo_path = self._app.resource_loader.get("LOGO_COLORED", "")
            if logo_path and Path(logo_path).exists():
                logo = Image(logo_path, width=0.89 * inch, height=0.5 * inch)
                logo.hAlign = 'CENTER'
                self._story.append(logo)
                self._story.append(Spacer(1, 0.1 * inch))
        except Exception:
            pass

    def _add_approval_section(self) -> None:
        chairman = self._file.chairman if self._file.chairman else "Фамилия И.О."

        data = [
            [Paragraph("Утверждаю", self._styles['Normal'])],
            [Paragraph("Председатель комиссии", self._styles['Normal'])],
            [Paragraph(f"______________________________________ {chairman}", self._styles['Normal'])],
            [Paragraph("______________________________20____г.", self._styles['Normal'])],
        ]

        table = Table(data, colWidths=[6 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        table.hAlign = "LEFT"

        self._story.append(table)
        self._story.append(Spacer(1, 0.2 * inch))

    def _add_title(self) -> None:
        title_text = f"Карта оценки риска №{self._file.map_no if self._file.map_no else '___'}"
        title = Paragraph(f"<b>{title_text}</b>", self._styles['CenterBold'])
        self._story.append(title)
        self._story.append(Spacer(1, 0.2 * inch))

    def _add_main_info(self) -> None:
        info_data = [
            ("1. Название профессии", self._file.profession if self._file.profession else ""),
            ("2. Наименование структурного подразделения", self._file.department if self._file.department else ""),
            ("3. Краткое описание выполняемой работы", self._file.description if self._file.description else ""),
            ("4. Используемое оборудование, материалы, сырье",
             self._file.tools_and_materials if self._file.tools_and_materials else "")
        ]

        for label, value in info_data:
            self._story.append(Paragraph(f"<b>{label}</b>", self._styles['Bold']))
            self._story.append(Paragraph(value, self._styles['Normal']))
            self._story.append(Spacer(1, 0.1 * inch))

        self._story.append(Paragraph("<b>5. Нормативные документы:</b>", self._styles['Bold']))
        if self._file.regulatory_docs:
            for doc in self._file.regulatory_docs:
                self._story.append(Paragraph(doc, self._styles['Normal']))
        else:
            self._story.append(Paragraph("", self._styles['Normal']))
        self._story.append(Spacer(1, 0.1 * inch))

    def _add_summary_table(self) -> None:
        self._story.append(Paragraph("<b>6. Сводные данные:</b>", self._styles['Bold']))
        self._story.append(Spacer(1, 0.1 * inch))

        data_dict = {
            "Уровень профессионального риска на рабочем месте по результатам оценки:":
                str(round(self._file.prof_risk, 2)) if self._file.prof_risk else '',
            "Показатель, учитывающий результаты специальной оценки условий труда:":
                str(self._file.k_factor) if self._file.k_factor is not None else '',
            "Итоговый уровень профессионального риска по результатам оценки:":
                str(round(self._file.result, 2)) if self._file.result else '',
            "По степени риска рабочее место отнесено к категории:":
                self._file.result_str if self._file.result_str else ''
        }

        table_data = []
        for desc, val in data_dict.items():
            table_data.append([
                Paragraph(desc, self._styles['Small']),
                Paragraph(val, self._styles['SmallCenter'])
            ])

        table = Table(table_data, colWidths=[4.5 * inch, 1.5 * inch])

        style_commands = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]

        if self._file.result_str:
            if self._file.result_str == "Высокий":
                style_commands.append(('TEXTCOLOR', (1, 3), (1, 3), colors.red))
            elif self._file.result_str == "Средний":
                style_commands.append(('TEXTCOLOR', (1, 3), (1, 3), colors.Color(252 / 255, 186 / 255, 3 / 255)))
            else:
                style_commands.append(('TEXTCOLOR', (1, 3), (1, 3), colors.green))

        table.setStyle(TableStyle(style_commands))
        self._story.append(table)
        self._story.append(Spacer(1, 0.2 * inch))

    def _add_risk_table(self) -> None:
        self._story.append(Paragraph("<b>7. Расчет уровней профессиональных рисков:</b>", self._styles['Bold']))
        self._story.append(Spacer(1, 0.1 * inch))

        headers = [
            '№ п/п', 'Номер опасности по перечню', 'Опасность', 'Опасное событие',
            'Качественное значение тяжести ущерба', 'Баллы по тяжести ущерба',
            'Качественное значение подверженности опасности', 'Баллы подверженности опасности',
            'Качественное значение вероятности возникновения опасности',
            'Вероятность возникновения опасности', 'Сумма весовых коэффициентов',
            'Весовой коэффициент вероятности возникновения опасности',
            'Риски по идентифицированным опасностям',
            'Оценка значимости риска по отдельной опасности'
        ]

        header_row = [Paragraph(f"<b>{h}</b>", self._styles['SmallCenterBold']) for h in headers]
        table_data = [header_row]

        weight_sum = sum(record.probability_pts for record in self._file.table) if self._file.table else 0

        for i, record in enumerate(self._file.table):
            row = [
                Paragraph(str(i + 1), self._styles['SmallCenter']),
                Paragraph(str(record.n) if record.n else '', self._styles['SmallCenter']),
                Paragraph(record.danger if record.danger else '', self._styles['Small']),
                Paragraph(record.event if record.event else '', self._styles['Small']),
                Paragraph(record.damage if record.damage else '', self._styles['SmallCenter']),
                Paragraph(str(record.damage_pts) if record.damage_pts else '', self._styles['SmallCenter']),
                Paragraph(record.susceptibility if record.susceptibility else '', self._styles['SmallCenter']),
                Paragraph(str(record.susceptibility_pts) if record.susceptibility_pts else '',
                          self._styles['SmallCenter']),
                Paragraph(record.probability if record.probability else '', self._styles['SmallCenter']),
                Paragraph(str(record.probability_pts) if record.probability_pts else '', self._styles['SmallCenter']),
                Paragraph(str(weight_sum) if i == 0 else '', self._styles['SmallCenter']),
                Paragraph(
                    str(round(record.probability_pts / weight_sum, 2))
                    if record.probability_pts and weight_sum else '',
                    self._styles['SmallCenter']
                ),
                Paragraph(str(record.identified_dangers_risks) if record.identified_dangers_risks else '',
                          self._styles['SmallCenter']),
                Paragraph(record.rating if record.rating else '', self._styles['SmallCenter'])
            ]
            table_data.append(row)

        col_widths = [0.4, 0.6, 2.2, 2.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        col_widths = [w * inch for w in col_widths]

        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))

        self._story.append(table)
        self._story.append(Spacer(1, 0.2 * inch))

    def _add_methods(self) -> None:
        self._story.append(Paragraph("<b>Общие меры по управлению рисками:</b>", self._styles['Bold']))

        if not self._file.methods:
            self._story.append(Paragraph("", self._styles['Normal']))
            return

        for method in self._file.methods:
            self._story.append(Paragraph(f"–  {method}", self._styles['Normal']))