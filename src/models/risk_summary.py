from src.core.file_system import File, FileIntegrityError
from src.models.risk_map import RiskMapFile
from src.utils.utils import normalize_path

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from PySide6.QtWidgets import QApplication
from typing import Optional, Self, Callable
import json, copy, gzip


class Entry:
    def __init__(self, app: QApplication, risk_map: RiskMapFile, on_modified_callback: Optional[Callable] = None):
        if not risk_map: raise ValueError("RiskMapFile object cannot be None.")

        self._app = app

        self._workplace_no: str = risk_map.map_no
        self._profession: str = risk_map.profession
        self._result: float = risk_map.result
        self._classification: str = risk_map.result_str

        self._reference_path = normalize_path(risk_map.save_path)
        self._content_checksum = self.checksum
        self._on_modified_callback = on_modified_callback

        if not self.is_filled: raise ValueError("Не заполнены критически важные поля.")

    @staticmethod
    def validate_path(path: Path | str) -> bool:
        path: Path = Path(path)
        if not path.exists(): return False
        if path.suffix != ".rskm": return False
        return True

    def validate_checksum(self) -> bool:
        risk_map = RiskMapFile.load_from_file(self._app, self._reference_path)
        if not risk_map: raise FileIntegrityError(f"Unable to initialize RiskMapFile object from {self._reference_path}.")

        stored_checksum = Entry.get_stored_checksum(risk_map)
        if stored_checksum != self._content_checksum: return False
        return True

    @property
    def is_filled(self) -> bool:
        return all([self._workplace_no, self._profession, self._reference_path, self._result,
                    self._classification, self._reference_path, self._content_checksum])

    def sync(self, risk_map: RiskMapFile) -> None:
        self._workplace_no = risk_map.map_no
        self._profession = risk_map.profession
        self._result = risk_map.result
        self._classification = risk_map.result_str
        self._content_checksum = self.checksum
        if self._on_modified_callback:
            self._on_modified_callback()

    @staticmethod
    def get_stored_checksum(risk_map: RiskMapFile) -> str:
        batch = {
            "n":            risk_map.map_no,
            "profession":   risk_map.profession,
            "result":       risk_map.result,
            "classification":   risk_map.result_str,
        }
        return File.calculate_checksum(batch)

    def _trigger_on_modification(self) -> None:
        if self._on_modified_callback:
            self._content_checksum = self.checksum
            self._on_modified_callback()

    @property
    def checksum(self) -> str:
        batch = {
            "n":            self._workplace_no,
            "profession":   self._profession,
            "result":       self._result,
            "classification":   self._classification,
        }
        return File.calculate_checksum(batch)

    @property
    def reference_path(self) -> str:
        return normalize_path(self._reference_path)

    @reference_path.setter
    def reference_path(self, reference_path: str) -> None:
        self._reference_path = reference_path
        self._on_modified_callback()

    @property
    def workplace_no(self) -> str:
        return self._workplace_no

    @workplace_no.setter
    def workplace_no(self, workplace_no: str) -> None:
        self._workplace_no = workplace_no
        self._on_modified_callback()

    @property
    def profession(self) -> str:
        return self._profession

    @profession.setter
    def profession(self, profession: str) -> None:
        self._profession = profession
        self._on_modified_callback()

    @property
    def result(self) -> float:
        return self._result

    @result.setter
    def result(self, result: float) -> None:
        self._result = result
        self._on_modified_callback()

    @property
    def classification(self) -> str:
        return self._classification

    @classification.setter
    def classification(self, classification: str) -> None:
        self._classification = classification
        self._on_modified_callback()

    @property
    def json(self) -> dict:
        return {
            "path":         self._reference_path,
            "checksum":     self._content_checksum,
            "n":            self._workplace_no,
            "profession":   self._profession,
            "result":       self._result,
            "classification":   self._classification,
        }


@dataclass
class Metadata:
    org_name: str = ""
    address: str = ""
    position: str = ""
    ceo: str = ""
    inn: str = ""
    okved: str = ""
    okato: str = ""
    chairman: str = ""


class RiskSummaryFile(File):
    _NEW_COUNTER = 0
    DEFAULT_NAME = "Новая сводная ведомость"

    def __init__(self, app: QApplication) -> None:
        File.__init__(self)

        self._app = app

        self._save_path: str = ""
        self._metadata: Metadata = Metadata()
        self._name: str = self.DEFAULT_NAME if not self._NEW_COUNTER else f"{self.DEFAULT_NAME} {self._NEW_COUNTER}"  # Mock
        self._entries_table: list[Entry] = []

        self._loaded_risk_maps: list[RiskMapFile] = []
        self._missing_paths_entries: list[dict] = []
        self._is_modified: bool = False

        RiskSummaryFile.increase_counter()

    def mark_modified(self):
        self._is_modified = True

    @classmethod
    def set_counter(cls, val: int) -> None:
        cls._NEW_COUNTER = val

    @classmethod
    def increase_counter(cls):
        cls._NEW_COUNTER += 1

    def __del__(self) -> None:
        self._NEW_COUNTER -= 1

    @property
    def entries_table(self) -> list[Entry]:
        return self._entries_table

    @entries_table.setter
    def entries_table(self, entries_table: Optional[list[Entry]]) -> None:
        if not entries_table: self._entries_table = []
        if not all(isinstance(ent, Entry) for ent in entries_table):
            raise ValueError(f'Unable to assign value to an attribute "table" with invalid type "{type(entries_table[0])}"')
        self._entries_table = entries_table

    def add_entry(self, risk_map: RiskMapFile) -> None:
        existing_checksum = Entry.get_stored_checksum(risk_map)
        if any(e.checksum == existing_checksum for e in self._entries_table):
            return

        self._entries_table.append(Entry(self._app, on_modified_callback=self.mark_modified, risk_map=risk_map))
        self._loaded_risk_maps.append(risk_map)
        self.mark_modified()

    def remove_entry(self, index: int) -> None:
        try:
            self._entries_table.pop(index)
            self.mark_modified()
        except IndexError: pass

    @property
    def missing_paths_entries(self) -> list[dict]:
        return self._missing_paths_entries

    def skip_all_missing_paths(self) -> None:
        self._missing_paths_entries = []

    @property
    def save_path(self) -> str:
        return self._save_path

    @save_path.setter
    def save_path(self, path: Path | str) -> None:
        self._save_path = normalize_path(path)

    @property
    def org_name(self) -> str:
        return self._metadata.org_name

    @org_name.setter
    def org_name(self, org_name: str) -> None:
        self._metadata.org_name = org_name
        self.mark_modified()

    @property
    def address(self) -> str:
        return self._metadata.address

    @address.setter
    def address(self, address: str) -> None:
        self._metadata.address = address
        self.mark_modified()

    @property
    def position(self) -> str:
        return self._metadata.position

    @position.setter
    def position(self, position: str) -> None:
        self._metadata.position = position
        self.mark_modified()

    @property
    def ceo(self) -> str:
        return self._metadata.ceo

    @ceo.setter
    def ceo(self, ceo: str) -> None:
        self._metadata.ceo = ceo
        self.mark_modified()

    @property
    def inn(self) -> str:
        return self._metadata.inn

    @inn.setter
    def inn(self, inn: str) -> None:
        if inn != "" and inn.isdigit() and (len(inn) == 10 or len(inn) == 12):
            self._metadata.inn = inn
            self.mark_modified()

    @property
    def okved(self) -> str:
        return self._metadata.okved

    @okved.setter
    def okved(self, okved: str) -> None:
        self._metadata.okved = okved
        self.mark_modified()

    @property
    def okato(self) -> str:
        return self._metadata.okato

    @okato.setter
    def okato(self, okato: str) -> None:
        self._metadata.okato = okato
        self.mark_modified()

    @property
    def chairman(self) -> str:
        return self._metadata.chairman

    @chairman.setter
    def chairman(self, chairman: str) -> None:
        self._metadata.chairman = chairman
        self.mark_modified()

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    @is_modified.setter
    def is_modified(self, is_modified: bool) -> None:
        self._is_modified = is_modified

    @property
    def tab_name(self) -> str:
        return f"{self.name}{"*" if self.is_modified else ""}.rsks"

    def form_registry(self) -> list[str]:
        registry = set()
        for risk_map in self._loaded_risk_maps:
            if not risk_map: continue
            stored_methods = set(risk_map.methods)
            registry.update(stored_methods)

        registry = list(registry)
        registry.sort()

        return registry

    def get_max_rate_events(self) -> dict:
        max_rate_events = defaultdict(float)
        for risk_map in self._loaded_risk_maps:
            if not risk_map: continue
            for record in risk_map.table:
                n, n_ = record.n, record.n_
                event = f"{n}.{n_} {record.event}"
                identified_dangers_risks = record.identified_dangers_risks
                max_rate_events[event] = max(max_rate_events.get(event, 0), identified_dangers_risks)

        return max_rate_events


    def save_to_file(self, save_path: Optional[Path | str], name: Optional[str] = None) -> bool:
        if not save_path or not Path(save_path).parent.exists(): return False
        save_path: Path = Path(save_path)

        self.save_path = normalize_path(save_path) if save_path.suffix == ".rsks" else normalize_path(f"{save_path.stem}.rsks")
        self.name = Path(self.save_path).stem if not name else name

        payload = {
            "org_name": self._metadata.org_name if self._metadata.org_name else "",
            "address":  self._metadata.address if self._metadata.address else "",
            "position": self._metadata.position if self._metadata.position else "",
            "ceo":      self._metadata.ceo if self._metadata.ceo else "",
            "inn":      self._metadata.inn if self._metadata.inn else "",
            "okved":    self._metadata.okved if self._metadata.okved else "",
            "okato":    self._metadata.okato if self._metadata.okato else "",
            "chairman": self._metadata.chairman if self._metadata.chairman else "",
            "table":    [record.json for record in self._entries_table]
        }

        container = self.create_container(payload)

        dump = json.dumps(container, ensure_ascii=False, indent=0)
        with gzip.open(self.save_path, 'wt', encoding='utf-8') as f:
            f.write(dump)

        self._is_modified = False
        return True

    @classmethod
    def load_from_file(cls, app: QApplication, open_path: Optional[Path | str]) -> Optional[Self]:
        if not open_path: return None
        open_path: Path = Path(open_path)

        if open_path.suffix == ".rsks" and open_path.exists() and open_path.is_file():
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

                risk_summary = cls(app)
                risk_summary._metadata.org_name = _payload.get("org_name", "")
                risk_summary._metadata.address = _payload.get("address", "")
                risk_summary._metadata.position = _payload.get("position", "")
                risk_summary._metadata.ceo = _payload.get("ceo", "")
                risk_summary._metadata.inn = _payload.get("inn", "")
                risk_summary._metadata.okved = _payload.get("okved", "")
                risk_summary._metadata.okato = _payload.get("okato", "")
                risk_summary._metadata.chairman = _payload.get("chairman", "")
                risk_summary._name = Path(open_path).stem

                tmp_table = []
                loaded_checksums = set()

                for entry_data in _payload.get("table", []):
                    stored_path = Path(entry_data.get("path", ""))

                    if not Entry.validate_path(stored_path):
                        risk_summary._missing_paths_entries.append(entry_data)
                        continue

                    loaded_risk_map = RiskMapFile.load_from_file(app, stored_path)
                    if not loaded_risk_map: continue

                    risk_summary._loaded_risk_maps.append(loaded_risk_map)
                    entry = Entry(app=app, on_modified_callback=risk_summary.mark_modified, risk_map=loaded_risk_map)

                    hashed_data = Entry.get_stored_checksum(loaded_risk_map)
                    if hashed_data in loaded_checksums: continue

                    entry.sync(loaded_risk_map)
                    loaded_checksums.add(hashed_data)
                    tmp_table.append(entry)

                risk_summary._entries_table = tmp_table
                risk_summary._save_path = normalize_path(open_path)
                risk_summary._is_modified = False
                return risk_summary

        else:
            return None

    def auto_save(self) -> bool:
        if self.is_modified and self.save_path:
            return self.save_to_file(save_path=self.save_path)
        return False

    @staticmethod
    def copy(other: 'RiskSummaryFile') -> 'RiskSummaryFile':
        return copy.deepcopy(other)
