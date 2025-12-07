import json, os
import gzip as gz
from .database import *
from .database import database as db
from typing import Optional
import copy
from pathlib import Path


#============== Строка таблицы ==============#
class Record:
#   Класс для хранения полей строки таблцы,
#   Pts-поля и n выставляются автоматически,
#   weight, identifiedDangerRisks и rating вычисляются
#   изменения передаются в параметр isModified класса Table
#   onModifiedCallback принимает в параметр функцию, меняющую стостояние триггера модификации
    def __init__(self, onModifiedCallback = None):
        self._n = None
        self._danger = None
        self._event = None
        self._damage = None
        self._damagePts = None
        self._susceptibility = None
        self._susceptibilityPts = None
        self._probability = None
        self._probabilityPts = None
        self._weight = None
        self._identifiedDangersRisks = None
        self._rating = None

        self.onModifiedCallback = onModifiedCallback

#======= Callback при изменении значений =======#
    def _triggerOnModification(self):
        if self.onModifiedCallback:
            self.onModifiedCallback()

#======= Геттеры и сеттеры =======#
#   При некорректном вводе геттеры выставляют по-дефолту None,
#   Сделано для надежности, хотя выбор значений и так происходит из заданных списков
    @property
    def n(self):
        return self._n

    @property
    def danger(self):
        return self._danger

    @danger.setter
    def danger(self, new_danger) -> None:
        if new_danger in list(db.database.keys()):
            self._danger = db.database[new_danger]["desc"]
            self._n = db.database[new_danger]["No"]
            self._event = None
            self._triggerOnModification()

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, newEvent):
        if self._danger is not None and newEvent in list(db.database[f'{self._n}. {self.danger}']["events"].keys()):
            self._event = newEvent
            self._triggerOnModification()

    @property
    def damage(self):
        return self._damage

    @property
    def damagePts(self):
        return self._damagePts

    @damage.setter
    def damage(self, newDamage) -> None:
        if newDamage in list(DAMAGE.keys()) and self._event is not None:
            self._damage = newDamage
            self._damagePts = DAMAGE[newDamage]
            self._triggerOnModification()

    @property
    def susceptibility(self):
        return self._susceptibility

    @property
    def susceptibilityPts(self):
        return self._susceptibilityPts

    @susceptibility.setter
    def susceptibility(self, newSusceptibility) -> None:
        if newSusceptibility in list(SUSCEPTIBILITY.keys()) and self._event is not None:
            self._susceptibility = newSusceptibility
            self._susceptibilityPts = SUSCEPTIBILITY[newSusceptibility]
            self._triggerOnModification()

    @property
    def probability(self):
        return self._probability

    @property
    def probabilityPts(self):
        return self._probabilityPts

    @probability.setter
    def probability(self, newProbability) -> None:
        if newProbability in list(PROBABILITY.keys()) and self._event is not None:
            self._probability = newProbability
            self._probabilityPts = PROBABILITY[newProbability]
            self._triggerOnModification()

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, newWeight: float) -> None:
        self._weight = round(float(newWeight), 2)
        self._triggerOnModification()

    @property
    def identifiedDangersRisks(self):
        return self._identifiedDangersRisks

    @identifiedDangersRisks.setter
    def identifiedDangersRisks(self, newIdentifiedDangersRisks: float) -> None:
        self._identifiedDangersRisks = round(float(newIdentifiedDangersRisks), 2)
        self._triggerOnModification()

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, newRating: str) -> None:
        self._rating = newRating
        self._triggerOnModification()

#======= Проверка записи на заполненность критически важных для вычислений полей и пустоту =======#
    def isNotFilled(self) -> bool:
        return (self._n is None) or (self._danger is None) or (self._event is None) or (self._damage is None) or (self._susceptibility is None)\
            or (self._probability is None) or (self._damagePts is None) or (self._susceptibilityPts is None) or (self._probabilityPts is None)

    def isEmpty(self) -> bool:
        return all((v is None or v == "") for v in vars(self).values())

#============== Таблица и её приложения ==============#
class Table:
#   Таблица-массив объектов Record и список методик реагирования на риски
#   Результаты вычислений описаны profRisk, result и resultStr
#   kFactor задается пользователем
#   регистрируются изменения"""
    def __init__(self):
        self._weightSum = None
        self.table: list[Record, ...] = []
        self.methods: list[str, ...] = []
        self._profRisk = None
        self._kFactor = 0.0
        self._result = None
        self._resultStr = None
        self._isModified = False
        self._methodModified = True

    def _markModified(self):
        self._isModified = True

#============== Геттеры и сеттеры, методы для добавления и удаления строк таблицы, удаления записи из списка методик ==============#
    @property
    def weightSum(self) -> int:
        return self._weightSum

    @weightSum.setter
    def weightSum(self, newWeightSum: int) -> None:
        self._weightSum = newWeightSum
        self._markModified()

    def tableAddRecord(self) -> None:
        self.table.append(Record(onModifiedCallback=self._markModified()))
        self._markModified()

    def tableRemoveRecord(self, index: int) -> None:
        self.table.pop(index)
        self._markModified()

    def methodsRemoveLine(self, index: int):
        self.methods.pop(index)
        self._markModified()

    @property
    def profRisk(self) -> float:
        return self._profRisk

    @property
    def kFactor(self) -> float:
        return self._kFactor

    @kFactor.setter
    def kFactor(self, newKFactor: float) -> None:
        if newKFactor in (-1.0, 0.0, 1.0):
            self._kFactor = newKFactor
            self._markModified()

    @property
    def result(self) -> float:
        return self._result

    @property
    def resultStr(self) -> str:
        return self._resultStr

    @property
    def isModified(self) -> bool:
        return self._isModified

#======= Вычисление результата =======#
#   Удаляются полностью пустые записи ->
#   Выполняется проверка на заполненность всех строк ->
#   Удаляются все записи-дубликаты, содержащие одинаковые номер, опасность и опасное событие ->
#   Проводятся вычисления ->
#   На основе вычислений формируются результат и список методик
    def calculate(self, updateMethods: bool = True) -> int:
        self.removeEmptyRecords()
        self._markModified()
        if not self.table:
            return -1
        else:
            fillFlag: bool = False
            for record in self.table:
                if record.isNotFilled():
                    fillFlag = True
                    break
            if not fillFlag:
                self.removeDuplicates()
                self.table.sort(key=lambda x: (int(x.n), x.danger))
                self.weightSum: int = sum(record.probabilityPts for record in self.table)
                for record in self.table:
                    record.weight = record.probabilityPts/self.weightSum
                    record.identifiedDangersRisks = round(record.damagePts * record.susceptibilityPts * record.probabilityPts / self.weightSum, 2)
                    record.rating ="Низкий" if record.identifiedDangersRisks <= 0.9 else \
                                  ("Умеренный" if record.identifiedDangersRisks <= 1.8 else "Высокий")
                profRisk: float = round(sum(record.identifiedDangersRisks for record in self.table), 2)
                self._profRisk = profRisk
                self._result = round(self._kFactor + self._profRisk, 2)
                self._resultStr = "Низкий" if self._result <= 10.0 else ("Средний" if self._result < 15 else "Высокий")
                if updateMethods:
                    self.fillMethods()
                self._markModified()
                return 1
            else:
                return 0

#======= Заполнение списка методик =======#
    def fillMethods(self):
        temp_methods: list[str, ...] = []
        for record in self.table:
            if (record.rating is not None) and (record.rating == "Умеренный" or record.rating == "Высокий"):
                temp_methods += db.database[f'{record.n}. {record.danger}']["events"][record.event]
        temp_methods = list(set(temp_methods))
        temp_methods.sort()
        if self.methods != temp_methods:
            self._methodModified = True
        self.methods = temp_methods.copy()

#======= Удаление дубликатов =======#
    def removeDuplicates(self) -> None:
        seen: set[tuple, ...] = set()
        unique_records: list[Record, ...] = []
        for record in self.table:
            key : tuple = (record.n, record.danger, record.event)
            if key not in seen:
                seen.add(key)
                unique_records.append(record)
        self.table = unique_records

#======= Удаление пустых записей =======#
    def removeEmptyRecords(self) -> None:
        if self.table:
            self.table = [record for record in self.table if not record.isEmpty()]


#============== Карта профессиональных рисков ==============#
class RiskMap(Table):
#   Класс для работы с картами: сериализации в *.rsk и конвертирования в отчет *.doc
#   Задаются дополнительные атрибуты для формирования отчета
#   Добавляются методы для автоматизированного и автоматического сохранения, загрузки объекта из файла"""
    _new_map_counter = 1
    def __init__(self):
        super().__init__()
        self._savePath = None
        self._mapNo = None
        self._chairman = None
        self._profession = None
        self._structDivision = None
        self._description = None
        self._toolsMaterials = None
        self._regulatoryDocs = REGULATORY_DOCS
        self._name = f"Новая карта {self._new_map_counter}"
        RiskMap._new_map_counter += 1

#======= Сеттеры и геттеры =======#
    @property
    def mapNo(self) -> str:
        return self._mapNo

    @mapNo.setter
    def mapNo(self, newMapNo: str):
        if newMapNo:
            if newMapNo.isdigit():
                self._mapNo = newMapNo
            else:
                self._mapNo = None
            self._markModified()

    @property
    def chairman(self):
        return self._chairman

    @chairman.setter
    def chairman(self, newChairman: str) -> None:
        self._chairman = newChairman
        self._markModified()

    @property
    def profession(self):
        return self._profession

    @profession.setter
    def profession(self, newProfession: str) -> None:
        self._profession = newProfession
        self._markModified()

    @property
    def structDivision(self):
        return self._structDivision

    @structDivision.setter
    def structDivision(self, newStructDivision: str) -> None:
        self._structDivision = newStructDivision
        self._markModified()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, newDescription: str) -> None:
        self._description = newDescription
        self._markModified()

    @property
    def toolsMaterials(self):
        return self._toolsMaterials

    @toolsMaterials.setter
    def toolsMaterials(self, newToolMaterials: str) -> None:
        self._toolsMaterials = newToolMaterials
        self._markModified()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, newName: str):
        if newName is not None:
            self._name = newName

    @property
    def savePath(self):
        return self._savePath

    @savePath.setter
    def savePath(self, newPath: str):
        if newPath is not None:
            self._savePath = newPath

    def getTabName(self) -> str:
        return f"{self.name}{"*" if self._isModified else ""}.rsk"

#======= Сериализация объекта в .rsk на основе JSON =======#
    def saveToRsk(self, path: str, compressed: bool = True, name: str = None) -> bool:
        if path:
            self._savePath = path if path.lower().endswith(".rsk") else path+".rsk"
        if not self._savePath:
            return False
        if name is None and self._name is None:
            name = Path(self._savePath).stem
        data = {
            "mapNo": str(self._mapNo) if self._mapNo is not None else self._mapNo,
            "chairman": self._chairman,
            "profession": self._profession,
            "structDivision": self._structDivision,
            "description": self._description,
            "toolsMaterials": self._toolsMaterials,
            "regulatoryDocs": self._regulatoryDocs,
            "kFactor": self._kFactor,
            "profRisk": self._profRisk,
            "result": self._result,
            "resultStr": self._resultStr,
            "name": name if name else self._name,
            "table": [
                {
                    "n": record.n,
                    "danger": record.danger,
                    "event": record.event,
                    "damage": record.damage,
                    "damagePts": record.damagePts,
                    "susceptibility": record.susceptibility,
                    "susceptibilityPts": record.susceptibilityPts,
                    "probability": record.probability,
                    "probabilityPts": record.probabilityPts,
                    "weight": record.weight,
                    "identifiedDangersRisks": record.identifiedDangersRisks,
                    "rating": record.rating,
                }
                for record in self.table
            ],
            "methods": self.methods
        }
        if compressed:
            jsonStr = json.dumps(data, ensure_ascii=False, indent=4)
            with gz.open(self._savePath, 'wt', encoding='utf-8') as f:
                f.write(jsonStr)
        else:
            with open(self._savePath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()
        self._isModified = False
        return True

#======= Чтение .rsk, создание нового объекта на основе сериализованных данных, добавление пути для автосохранения =======#
    @classmethod
    def loadFromRsk(cls, path:str, compressed:bool=True) -> Optional['RiskMap']:
        if path.lower().endswith(".rsk") and os.path.exists(path) and os.path.isfile(path) and (path is not None):
            if compressed:
                f = gz.open(path, 'rt', encoding='utf-8')
            else:
                f = open(path, 'r', encoding='utf-8')
            data = json.load(f)
            riskMap = cls()
            riskMap.name = os.path.split(path)[1].removesuffix(".rsk")
            riskMap.mapNo = data.get("mapNo")
            riskMap.chairman = data.get("chairman")
            riskMap.profession = data.get("profession")
            riskMap.structDivision = data.get("structDivision")
            riskMap.description = data.get("description")
            riskMap.toolsMaterials = data.get("toolsMaterials")
            riskMap.kFactor = data.get("kFactor")
            riskMap._profRisk = data.get("profRisk")
            riskMap._result = data.get("result")
            riskMap._resultStr = data.get("resultStr")
            riskMap.methods = data.get("methods")
            riskMap.name = data.get("name")
            riskMap.table = []
            for recordData in data.get("table", []):
                record = Record(onModifiedCallback=riskMap._markModified())
                record._n = recordData.get("n")
                record._danger = recordData.get("danger")
                record._event = recordData.get("event")
                record._damage = recordData.get("damage")
                record._damagePts = recordData.get("damagePts")
                record._susceptibility = recordData.get("susceptibility")
                record._susceptibilityPts = recordData.get("susceptibilityPts")
                record._probability = recordData.get("probability")
                record._probabilityPts = recordData.get("probabilityPts")
                record._weight = recordData.get("weight")
                record._identifiedDangersRisks = recordData.get("identifiedDangersRisks")
                record._rating = recordData.get("rating")
                riskMap.table.append(record)
            riskMap._savePath = path
            riskMap._isModified = False
            f.close()
            return riskMap
        else:
            return

#======= Автосохранение файла =======#
    def autoSave(self, compressed: bool = True) -> bool:
        if self._isModified and self._savePath:
            return self.saveToRsk(self._savePath, compressed=compressed)
        return False

    @staticmethod
    def copy(other: 'RiskMap') -> 'RiskMap':
        return copy.deepcopy(other)
