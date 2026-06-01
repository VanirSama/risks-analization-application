from pathlib import Path
from typing import Optional
import os


def clamp(x: float| int, min_x: Optional[float | int], max_x: Optional[float | int]) -> float | int:
    if not min_x and not max_x: raise ValueError("Clamping must have at least one limit.")
    if not min_x: return min(x, max_x)
    if not max_x: return max(min_x, x)

    if min_x > max_x: raise ValueError("Higher clamping limit can not be less than lesser limit.")
    return max(min_x, min(max_x, x))

def normalize_path(path: Path | str) -> str:
    return os.path.normcase(Path(path))


class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]