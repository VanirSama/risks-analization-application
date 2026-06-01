from src.utils.utils import SingletonMeta

from PySide6.QtWidgets import QApplication
from typing import Optional, Any
import json


class DatabaseManager(metaclass=SingletonMeta):
	_FALLBACK = {
		"1. Опасность": {
			"Событие": ["Мера"]
		}}

	DAMAGE = {
		"Незначительный ущерб": 1,
		"Малый ущерб": 2,
		"Средний ущерб": 3,
		"Большой ущерб": 4,
		"Очень большой ущерб": 5
	}

	SUSCEPTIBILITY = {
		"Очень редко": 1,
		"Редко": 2,
		"Иногда": 3,
		"Часто": 4,
		"Постоянно": 5
	}

	PROBABILITY = {
		"Почти невозможно": 1,
		"Вряд ли возможно": 2,
		"Маловероятно": 3,
		"Возможно": 4,
		"Очень вероятно": 5
	}

	REGULATORY_DOCS = [
		"ГОСТ 12.0.003-2015. Межгосударственный стандарт. Система стандартов безопасности труда. Опасные и вредные производственные факторы. Классификация",
		"ГОСТ Р 12.0.007-2009. Система стандартов безопасности труда. Система управления охраной труда в организации. Общие требования по разработке, применению, оценке и совершенствованию",
		"ГОСТ Р 12.0.010-2009. Национальный стандарт Российской Федерации. Система стандартов безопасности труда. Системы управления охраной труда. Определение опасностей и оценка рисков",
		"Приказ Минтруда РФ от 31.01.2022 N 36 \"Об утверждении рекомендаций по классификации, обнаружению, распознаванию и описанию опасностей\"",
		"Приказ Минтруда РФ от 28.12.2021 N 926 \"Об утверждении рекомендаций по выбору методов оценки уровней профессиональных рисков и по снижению уровней таких рисков\"",
		"Приказ Минтруда РФ от 29.10.2021 N 776н \"Об утверждении примерного положения о системе управления охраной труда\""
	]

	def __init__(self, app: QApplication) -> None:
		self._app = app

		try:
			self.reg: dict = self.load_registry()
			if not self.reg:
				self.reg = self._FALLBACK

		except FileNotFoundError | PermissionError:
			# Fallback
			self.reg = self._FALLBACK

	def load_registry(self) -> Optional[dict[str, Any]]:
		with open(self._app.resource_loader.get("DATABASE_FILE", ""), mode="r", encoding="utf-8") as f:
			return json.load(f)

	@property
	def dangers(self) -> list[str]:
		return list(self.reg.keys())

	def get_events(self, danger: Optional[str] = None) -> Optional[list[str]]:
		if danger and danger in self.reg:
			return list(self.reg.get(danger, {}).keys())
		return None


# DATABASE = DatabaseManager()
