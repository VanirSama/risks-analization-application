from src.core.file_system import File
from src.models.risk_map import RiskMapFile
from src.models.risk_summary import RiskSummaryFile
from src.ui.risk_tabs import RiskMapTab, RiskSummaryTab
from src.utils.resources import ResourceLoader



class FileMapping:
    RECENT_FILES_ICONS = {
        ".rskm":    ResourceLoader.RSKM_DOC_ICON,
        ".rsks":    ResourceLoader.RSKS_DOC_ICON,
    }

    EXTENSIONS_TO_CLASSES = {
        ".rskm":    RiskMapFile,
        ".rsks":    RiskSummaryFile,
    }

    TABS_CLASSES = {
        RiskMapFile:        RiskMapTab,
        RiskSummaryFile:    RiskSummaryTab,
    }

    CLASS_TO_EXTENSIONS = {
        RiskMapFile:        {"filter": "Файлы карт рисков (*.rskm)", "extension": ".rskm"},
        RiskSummaryFile:    {"filter": "Файлы сводных ведомостей (*.rsks)", "extension": ".rsks"},
    }

    @classmethod
    def get_file_class(cls, obj: File) -> File:
        for c in cls.EXTENSIONS_TO_CLASSES.values():
            if isinstance(obj, c): return c
        return File