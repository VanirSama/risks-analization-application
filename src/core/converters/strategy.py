from src.core.converters.base import Converter
from src.core.converters.docx import RiskMapToDocxConverter
from src.core.converters.pdf import RiskMapToPdfConverter

from PySide6.QtWidgets import QApplication
from typing import Type


class ConverterStrategy:
    _registry = {}

    def __init__(self, app: QApplication):
        self._app = app

    @classmethod
    def get_converter_by_filter(cls, filter_string: str) -> Type[Converter] | None:
        return cls._registry.get(filter_string, None)

    @classmethod
    def get_all_filters(cls) -> str:
        return ";;".join(cls._registry.keys())

    def create_converter(self, filter_string: str, item):
        converter_class = self.get_converter_by_filter(filter_string)
        if converter_class:
            return converter_class(self._app, item)
        return None


class RiskMapConverterStrategy(ConverterStrategy):
    _registry: dict[str, tuple[Type[Converter], str]] = {
        # filter_string: ConverterClass
        "Документы MS Word (*.docx)":   RiskMapToDocxConverter,
        "Документы PDF (*.pdf)":        RiskMapToPdfConverter,
    }