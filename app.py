from src.config.config_manager import ConfigManager
from src.core.database.manager import DatabaseManager
from src.services.error_handler import ErrorHandler
from src.ui.components.splash import SplashScreen
from src.ui.styles.fonts import load_fonts
from src.ui.main_window import MainWindow
from src.utils.resources import ResourceLoader
from src.utils.utils import normalize_path
from src.__version__ import get_version_info

from pathlib import Path
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
import sys, os


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def get_env_path() -> str:
    if getattr(sys, 'frozen', False): return normalize_path(Path(sys._MEIPASS) / ".env")
    else: return normalize_path(Path(__file__).resolve().parent.parent.parent / ".env")


class AuraApp(QApplication):
    def __init__(self) -> None:
        super().__init__(sys.argv)

        self.resource_loader                = ResourceLoader(self)
        self.database_manager               = DatabaseManager(self)
        self.config_manager                 = ConfigManager(self)

        self._file_to_open: Path | None     = None
        self._error_handler                 = None
        self._main_window                   = None

        if len(sys.argv) > 1:
            if sys.argv[1] == '--register':
                sys.exit(0x0)
            else:
                arg_path = Path(sys.argv[1])

                if not arg_path.exists():
                    raise FileNotFoundError(f'Could not find file "{arg_path}"')

                if not arg_path.is_file():
                    raise ValueError(f'Could not open "{arg_path}" as file')

                if arg_path.suffix not in [".rskm", ".rsks"]:
                    raise ValueError( f'Could not open file "{arg_path}" with {get_version_info()}')

                self._file_to_open = arg_path

        self._validate_license()

        self._splash = SplashScreen(self)
        self._splash.show()

    # TODO
    def _validate_license(self) -> None: ...

    def _setup(self) -> None:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=get_env_path())
        load_fonts(self)

        self._main_window = MainWindow(self, get_version_info())

        if self._file_to_open:
            self._main_window.open_file_from_args(self._file_to_open)

        self._main_window.showMaximized()
        self._splash.finish(self._main_window)

    def run(self) -> None:
        QTimer.singleShot(750, self._setup)
        self.exec()

    @property
    def error_handler(self) -> ErrorHandler:
        return self._error_handler

    @error_handler.setter
    def error_handler(self, handler: ErrorHandler) -> None:
        self._error_handler = handler


if __name__ == '__main__':
    if sys.version_info < (3, 11):
        raise RuntimeError("API server cannot run using Python interpreter with version lower than 3.11.X")

    app = AuraApp()
    with ErrorHandler(app) as error_handler:
        app.error_handler = error_handler
        app.run()
