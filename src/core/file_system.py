from src.utils.utils import normalize_path

from abc import ABC, abstractmethod
from hashlib import sha256
from pathlib import Path
from typing import Self, Optional, TypeVar
from PySide6.QtWidgets import QApplication
import json


class FileIntegrityError(OSError):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

    def __repr__(self):
        return self.msg


class File(ABC):
    DEFAULT_NAME = ""
    def __init__(self):
        self._name = ""
        self._save_path = ""

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        if name: self._name = name

    @property
    def save_path(self) -> str:
        return self._save_path

    @save_path.setter
    def save_path(self, save_path: Optional[Path | str]) -> None:
        if not save_path: return
        self._save_path = normalize_path(save_path)

    @abstractmethod
    def save_to_file(self, save_path: Optional[Path | str], name: Optional[str] = None) -> bool:
        pass

    @classmethod
    @abstractmethod
    def load_from_file(cls, app: QApplication, open_path: Optional[Path | str]) -> Optional[Self]:
        pass

    @staticmethod
    def calculate_checksum(data: dict) -> str:
        json_bytes = json.dumps(data, sort_keys=True, ensure_ascii=False).encode('utf-8')
        return sha256(json_bytes).hexdigest()

    def create_container(self, payload: dict) -> dict:
        checksum = self.calculate_checksum(payload)
        return {"payload": payload, "checksum": checksum}

TFile = TypeVar("TFile", bound=File)