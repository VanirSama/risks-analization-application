from typing import Optional
import json
from pathlib import Path

class DatabaseManager:
	def __init__(self):
		self.database: dict = self.load_database()
		if not self.database:
			self.database = {
				"1. Опасность": {
					"No": "1",
					"desc": "Описание",
					"events": {
						"Событие": ["Мера"]
					}
				}
			}

	@staticmethod
	def load_database() -> dict:
		with open(Path("backend/db.json").resolve(), mode="r", encoding="utf-8") as f:
			database: dict = json.load(f)
		return database

	def getDangers(self) -> list:
		return list(self.database.keys())

	def getDangerSubstats(self, danger: str) -> Optional[list[str, str]]:
		if danger in list(self.database.keys()):
			return [self.database[danger]["No"], danger]
		return None

	def getEvents(self, danger: Optional[str] = None) -> Optional[list[str, ...]]:
		if danger in list(self.database.keys()):
			return list(self.database[danger]["events"].keys())
		return []

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

database = DatabaseManager()
