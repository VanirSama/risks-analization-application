from src.core.database.manager import DatabaseManager
from src.core.file_system import File, FileIntegrityError
from src.utils.utils import normalize_path

from dataclasses import dataclass
from pathlib import Path
from PySide6.QtWidgets import QApplication
from typing import Optional, Callable, Self
import json, copy, gzip


class Record:
    def __init__(self, app: QApplication, on_modified_callback: Optional[Callable] = None):
        self._app = app
        self._n: str = ""
        self._danger: str = ""
        self._n_: str = ""
        self._event: str = ""

        self._damage: str = ""
        self._damage_pts: int = 0

        self._susceptibility: str = ""
        self._susceptibility_pts: int = 0

        self._probability: str = ""
        self._probability_pts: int = 0

        self._weight: float = 0.0
        self._identified_dangers_risks: float = 0.0
        self._rating: str = ""

        self._on_modified_callback = on_modified_callback

    def _trigger_on_modification(self) -> None:
        if self._on_modified_callback:
            self._on_modified_callback()

    @property
    def n(self) -> str:
        return self._n

    @n.setter
    def n(self, n: int | str) -> None:
        self._n = str(n)

    @property
    def danger(self) -> str:
        return self._danger

    @danger.setter
    def danger(self, danger: str) -> None:
        if danger in self._app.database_manager.dangers:
            self._n, self._danger = danger.split(" ", 1)
            self._event = ""
            self._trigger_on_modification()

    @property
    def n_(self) -> str:
        return self._n_

    @n_.setter
    def n_(self, n_: int | str) -> None:
        self._n_ = str(n_)

    @property
    def event(self) -> str:
        return self._event

    @event.setter
    def event(self, event) -> None:
        if self._danger and event in self._app.database_manager.get_events(f"{self._n}. {self._danger}"):
            self._n_, self._event = event.split(" ", 1)
            self._trigger_on_modification()

    @property
    def damage(self) -> str:
        return self._damage

    @property
    def damage_pts(self) -> int:
        return self._damage_pts

    @damage.setter
    def damage(self, damage) -> None:
        if damage in DatabaseManager.DAMAGE and self._event:
            self._damage = damage
            self.damage_pts = DatabaseManager.DAMAGE[damage]
            self._trigger_on_modification()

    @damage_pts.setter
    def damage_pts(self, damage_pts: int) -> None:
        self._damage_pts = damage_pts

    @property
    def susceptibility(self) -> str:
        return self._susceptibility

    @property
    def susceptibility_pts(self) -> int:
        return self._susceptibility_pts

    @susceptibility.setter
    def susceptibility(self, susceptibility) -> None:
        if susceptibility in DatabaseManager.SUSCEPTIBILITY and self._event:
            self._susceptibility = susceptibility
            self.susceptibility_pts = DatabaseManager.SUSCEPTIBILITY[susceptibility]
            self._trigger_on_modification()

    @susceptibility_pts.setter
    def susceptibility_pts(self, susceptibility_pts) -> None:
        self._susceptibility_pts = susceptibility_pts

    @property
    def probability(self) -> str:
        return self._probability

    @property
    def probability_pts(self) -> int:
        return self._probability_pts

    @probability.setter
    def probability(self, probability) -> None:
        if probability in DatabaseManager.PROBABILITY and self._event:
            self._probability = probability
            self.probability_pts = DatabaseManager.PROBABILITY[probability]
            self._trigger_on_modification()

    @probability_pts.setter
    def probability_pts(self, probability_pts) -> None:
        self._probability_pts = probability_pts

    @property
    def weight(self) -> float:
        return self._weight

    @weight.setter
    def weight(self, weight: float) -> None:
        self._weight = round(weight, 2)
        self._trigger_on_modification()

    @property
    def identified_dangers_risks(self) -> float:
        return self._identified_dangers_risks

    @identified_dangers_risks.setter
    def identified_dangers_risks(self, identified_dangers_risks: float) -> None:
        self._identified_dangers_risks = round(identified_dangers_risks, 2)
        self._trigger_on_modification()

    @property
    def rating(self) -> str:
        return self._rating

    @rating.setter
    def rating(self, rating: str) -> None:
        self._rating = rating
        self._trigger_on_modification()

    @property
    def is_complete(self) -> bool:
        return all([
            self._n, self._danger, self._n_, self._event, self._damage,
            self._susceptibility, self._probability, self._damage_pts,
            self._susceptibility_pts, self._probability_pts
        ])

    @property
    def is_empty(self) -> bool:
        return all(not v for k, v in vars(self).items() if not callable(v))

    @property
    def json(self) -> dict:
        return {
            "n":                        self._n,
            "danger":                   self._danger,
            "n_":                       self._n_,
            "event":                    self._event,
            "damage":                   self._damage,
            "damage_pts":               self._damage_pts,
            "susceptibility":           self._susceptibility,
            "susceptibility_pts":       self._susceptibility_pts,
            "probability":              self._probability,
            "probability_pts":          self._probability_pts,
            "weight":                   self._weight,
            "identified_dangers_risks": self._identified_dangers_risks,
            "rating":                   self._rating,
        }


class RecordsTable:
    def __init__(self, app: QApplication):
        self._app = app

        self._weight_sum: float = 0.0

        self._table: list[Record] = []
        self._methods: list[str] = []

        self._prof_risk: float = 0.0
        self._k_factor = 0.0
        self._result: float = 0.0
        self._result_str: str = ""

        self._is_modified: bool = False
        self._method_modified: bool = True

    def mark_modified(self):
        self._is_modified = True

    @property
    def weight_sum(self) -> int:
        return self._weight_sum

    @weight_sum.setter
    def weight_sum(self, weight_sum: int) -> None:
        self._weight_sum = weight_sum
        self.mark_modified()

    @property
    def table(self) -> list[Record]:
        return self._table

    @table.setter
    def table(self, table: list[Record]) -> None:
        if not table: return
        if not all(isinstance(rec, Record) for rec in table):
            raise ValueError(f'Unable to assign value to an attribute "table" with invalid type "{type(table[0])}"')
        self._table = table

    @property
    def methods(self) -> list[str]:
        return self._methods

    @methods.setter
    def methods(self, methods: list[str]) -> None:
        self._methods = methods
        self.mark_modified()

    def add_record(self) -> None:
        self.table.append(Record(app=self._app, on_modified_callback=self.mark_modified))
        self.mark_modified()

    def remove_record(self, index: int) -> None:
        try:
            self.table.pop(index)
            self.mark_modified()
        except IndexError: pass

    def methods_remove_line(self, index: int) -> None:
        try:
            self.methods.pop(index)
            self.mark_modified()
        except IndexError: pass

    @property
    def prof_risk(self) -> float:
        return self._prof_risk

    @prof_risk.setter
    def prof_risk(self, prof_risk: float) -> None:
        self._prof_risk = prof_risk

    @property
    def k_factor(self) -> float:
        return self._k_factor if self._k_factor is not None else 0.0

    @k_factor.setter
    def k_factor(self, k_factor: float) -> None:
        if k_factor is not None: self._k_factor = k_factor
        else: self._k_factor = 0.0 # Fallback
        self.mark_modified()

    @property
    def result(self) -> float:
        return self._result

    @result.setter
    def result(self, result: float) -> None:
        self._result = result

    @property
    def result_str(self) -> str:
        return self._result_str

    @result_str.setter
    def result_str(self, result_str: str) -> None:
        self._result_str = result_str

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, is_modified: bool) -> None:
        self._is_modified = is_modified

    @property
    def method_modified(self) -> bool:
        return self._method_modified

    @method_modified.setter
    def method_modified(self, method_modified: bool) -> None:
        self._method_modified = method_modified

    def calculate(self, update_methods: bool = True) -> int:
        self._remove_empty_records()
        self.mark_modified()

        if not self.table: return -1

        if all(record.is_complete for record in self._table):
            self._remove_duplicates()
            self.table.sort(key=lambda x: (int(x.n), x.danger))
            self.weight_sum: int = sum(record.probability_pts for record in self._table)

            for record in self.table:
                record.weight = record.probability_pts / self.weight_sum
                record.identified_dangers_risks = round(record.damage_pts * record.susceptibility_pts * record.probability_pts / self.weight_sum, 2)
                record.rating ="Низкий" if record.identified_dangers_risks <= 0.9 else ("Умеренный" if record.identified_dangers_risks <= 1.8 else "Высокий")

            self._prof_risk = round(sum(record.identified_dangers_risks for record in self._table), 2)
            self._result = round(self.k_factor + self.prof_risk, 2)

            self._result_str = "Низкий" if self._result <= 10.0 else ("Средний" if self._result < 15.0 else "Высокий")

            if update_methods:
                self._fill_methods()

            return 1

        else:
            return 0

    def _fill_methods(self) -> None:
        tmp: list[str] = []

        for record in self.table:
            if record.rating == "Умеренный" or record.rating == "Высокий":
                tmp.extend(self._app.database_manager.reg.get(f'{record.n}. {record.danger}').get(f'{record.n_} {record.event}'))

        temp_methods = list(set(tmp))
        temp_methods.sort()

        if self.methods != tmp:
            self.method_modified = True

        self.methods = temp_methods.copy()

    def _remove_duplicates(self) -> None:
        found: set[tuple] = set()
        unique_records: list[Record] = []

        for record in self._table:
            key: tuple = (record.n, record.danger, record.event)
            if key not in found:
                found.add(key)
                unique_records.append(record)

        self._table = unique_records

    def _remove_empty_records(self) -> None:
        if self._table:
            self.table = [record for record in self._table if not record.is_empty]


@dataclass
class Metadata:
    map_no: str = ""
    chairman: str = ""
    profession: str = ""
    department: str = ""
    description: str = ""
    tools_and_materials: str = ""


class RiskMapFile(File, RecordsTable):
    _NEW_COUNTER = 0
    DEFAULT_NAME = "Новая карта"

    def __init__(self, app: QApplication):
        File.__init__(self)
        RecordsTable.__init__(self, app)
        self._save_path: str = ""
        self._metadata = Metadata()
        self._regulatory_docs: list = DatabaseManager.REGULATORY_DOCS
        self._name = self.DEFAULT_NAME if not self._NEW_COUNTER else f"{self.DEFAULT_NAME} {self._NEW_COUNTER}" # Mock
        RiskMapFile.increase_counter()

    @classmethod
    def set_counter(cls, val: int) -> None:
        cls._NEW_COUNTER = val

    @classmethod
    def increase_counter(cls):
        cls._NEW_COUNTER += 1

    def __del__(self) -> None:
        self._NEW_COUNTER -= 1

    @property
    def save_path(self) -> str:
        return self._save_path

    @save_path.setter
    def save_path(self, path: Path | str) -> None:
        self._save_path = normalize_path(path)

    @property
    def map_no(self) -> str:
        return self._metadata.map_no

    @map_no.setter
    def map_no(self, map_no: str) -> None:
        if not map_no: return
        self._metadata.map_no = map_no
        self.mark_modified()

    @property
    def chairman(self) -> str:
        return self._metadata.chairman

    @chairman.setter
    def chairman(self, chairman: str) -> None:
        self._metadata.chairman = chairman
        self.mark_modified()

    @property
    def profession(self) -> str:
        return self._metadata.profession

    @profession.setter
    def profession(self, profession: str) -> None:
        self._metadata.profession = profession
        self.mark_modified()

    @property
    def department(self) -> str:
        return self._metadata.department

    @department.setter
    def department(self, department: str) -> None:
        self._metadata.department = department
        self.mark_modified()

    @property
    def description(self) -> str:
        return self._metadata.description

    @description.setter
    def description(self, description: str) -> None:
        self._metadata.description = description
        self.mark_modified()

    @property
    def tools_and_materials(self) -> str:
        return self._metadata.tools_and_materials

    @tools_and_materials.setter
    def tools_and_materials(self, tools_and_materials: str) -> None:
        self._metadata.tools_and_materials = tools_and_materials
        self.mark_modified()

    @property
    def regulatory_docs(self) -> str:
        return self._regulatory_docs

    @property
    def tab_name(self) -> str:
        return f"{self.name}{"*" if self.is_modified else ""}.rskm"

    def save_to_file(self, save_path: Optional[Path | str], name: Optional[str]=None) -> bool:
        if not save_path or not Path(save_path).parent.exists(): return False
        save_path: Path = Path(save_path)

        self.save_path = normalize_path(save_path) if save_path.suffix == ".rskm" else normalize_path(f"{save_path.stem}.rskm")
        self.name = Path(self.save_path).stem if not name else name

        payload = {
            "map_no":               self.map_no if self.map_no else "",
            "chairman":             self.chairman if self.chairman else "",
            "profession":           self.profession if self.profession else "",
            "department":           self.department if self.department else "",
            "description":          self.description if self.description else "",
            "tools_and_materials":  self.tools_and_materials if self.tools_and_materials else "",
            "regulatory_docs":      self._regulatory_docs if self._regulatory_docs else "",
            "k_factor":             self.k_factor if self.k_factor else 0.0,
            "prof_risk":            self.prof_risk if self.prof_risk else 0.0,
            "result":               self.result if self.result_str else 0.0,
            "result_str":           self.result_str if self.result_str else "",
            "name":                 self.name if self.name else f"Карта N ",
            "table":                [record.json for record in self._table],
            "methods":              self.methods if self.methods else []
        }

        container = self.create_container(payload)

        dump = json.dumps(container, ensure_ascii=False, indent=0)
        with gzip.open(self.save_path, 'wt', encoding='utf-8') as f:
            f.write(dump)

        self.is_modified = False
        return True

    @classmethod
    def load_from_file(cls, app: QApplication, open_path: Optional[Path | str]) -> Optional[Self]:
        if not open_path: return None
        open_path: Path = Path(open_path)

        if open_path.suffix == ".rskm" and open_path.exists() and open_path.is_file():
            with gzip.open(open_path, 'rt', encoding='utf-8') as f:
                contents = json.load(f)

                # Для совместимости со старым форматом без контрольной суммы
                _payload: dict = {}
                _stored_checksum: str = ""

                if "payload" not in contents or "checksum" not in contents:
                    _payload = contents
                else:
                    _stored_checksum = contents["checksum"]
                    _payload = contents["payload"]

                if _stored_checksum:
                    calculated_checksum = cls.calculate_checksum(_payload)
                    if _stored_checksum != calculated_checksum:
                        raise FileIntegrityError("Unable to read corrupted file")

                risk_map = cls(app)
                risk_map._metadata.map_no = _payload.get("map_no", "")
                risk_map._metadata.chairman = _payload.get("chairman", "")
                risk_map._metadata.profession = _payload.get("profession", "")
                risk_map._metadata.department = _payload.get("department", "")
                risk_map._metadata.description = _payload.get("description", "")
                risk_map._metadata.tools_and_materials = _payload.get("tools_and_materials", "")
                risk_map._metadata.regulatory_docs = _payload.get("regulatory_docs", [])
                risk_map._k_factor = _payload.get("k_factor", 0.0)
                risk_map._prof_risk = _payload.get("prof_risk", 0.0)
                risk_map._result = _payload.get("result", 0.0)
                risk_map._result_str = _payload.get("result_str", "")
                risk_map._methods = _payload.get("methods", [])
                risk_map._name = open_path.stem
                tmp_table = []
                for record_data in _payload.get("table", []):
                    record = Record(risk_map._app, on_modified_callback=risk_map.mark_modified)
                    record._n = record_data.get("n", "")
                    record._danger = record_data.get("danger", "")
                    record._n_ = record_data.get("n_", "")
                    record._event = record_data.get("event", "")
                    record._damage = record_data.get("damage", "")
                    record._damage_pts = record_data.get("damage_pts", 0)
                    record._susceptibility = record_data.get("susceptibility", "")
                    record._susceptibility_pts = record_data.get("susceptibility_pts", 0)
                    record._probability = record_data.get("probability", "")
                    record._probability_pts = record_data.get("probability_pts", 0)
                    record._weight = record_data.get("weight", 0.0)
                    record._identified_dangers_risks = record_data.get("identified_dangers_risks", 0.0)
                    record._rating = record_data.get("rating", "")
                    tmp_table.append(record)
                risk_map._table = tmp_table
                risk_map._save_path = normalize_path(open_path)
                risk_map._is_modified = False
                return risk_map

        else: return None

    def auto_save(self) -> bool:
        if self.is_modified and self.save_path:
            return self.save_to_file(save_path=self.save_path)
        return False

    @staticmethod
    def copy(other: 'RiskMapFile') -> 'RiskMapFile':
        return copy.deepcopy(other)