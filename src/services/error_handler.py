from src.core.file_system import FileIntegrityError

from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QApplication
from types import TracebackType
from typing import Type, Optional, Callable
import sys, traceback, logging


class ErrorHandler:
    _LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    _DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    _HANDLEABLE_ERRORS = (FileNotFoundError, PermissionError, ValueError, TypeError, OSError, MemoryError, KeyboardInterrupt,
        RuntimeError, ImportError, AttributeError, IndexError, KeyError, FileIntegrityError)

    def __init__(self, app: Optional[QApplication] = None, log_to_file: bool = True, show_dialog: bool = True,
            log_dir: Optional[Path] = None, exit_on_critical: bool = True) -> None:

        self._app = app
        _log_file = self._app.resource_loader.get("CRASHLOG")
        self._log_to_file = log_to_file
        self._show_dialog = show_dialog
        self._exit_on_critical = exit_on_critical
        self._log_file = log_dir or _log_file

        self._original_excepthook = None
        self._logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger("AuraErrorHandler")
        logger.setLevel(logging.DEBUG)

        logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter(self._LOG_FORMAT, self._DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        if self._log_to_file:
            try:
                file_handler = logging.FileHandler(
                    self._log_file, mode="a", encoding="utf-8"
                )
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(self._LOG_FORMAT, self._DATE_FORMAT)
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)
            except OSError as e:
                logger.warning(f"Could not write error traceback to log file: {e}")

        return logger

    def __enter__(self) -> "ErrorHandler":
        self._install_global_hooks()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> bool:

        self._uninstall_global_hooks()

        if exc_type is None:
            return False

        if exc_type is KeyboardInterrupt:
            self._logger.info("Manual Shutdown (User's input: Ctrl + C")
            return False

        if exc_type is SystemExit:
            self._logger.info(f"System Exit: {exc_val}")
            return False

        self._handle_exception(exc_type.__name__, exc_val, exc_tb)

        return True

    def _install_global_hooks(self) -> None:
        self._original_excepthook = sys.excepthook
        sys.excepthook = self._global_excepthook

    def _uninstall_global_hooks(self) -> None:
        if self._original_excepthook is not None:
            sys.excepthook = self._original_excepthook
            self._original_excepthook = None

    def _global_excepthook(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: Optional[TracebackType]) -> None:

        if issubclass(exc_type, KeyboardInterrupt):
            if self._original_excepthook:
                self._original_excepthook(exc_type, exc_val, exc_tb)
            return

        self._handle_exception(exc_type, exc_val, exc_tb)

    def _handle_exception(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: Optional[TracebackType]) -> None:
        self._last_error = exc_val

        tb_lines = traceback.format_exception(exc_type, exc_val, exc_tb)
        tb_text = "".join(tb_lines)

        is_critical = ErrorHandler._is_critical(exc_type)
        severity = "CRITICAL" if is_critical else "ERROR"

        user_message = self._get_user_message(exc_type, exc_val)

        self._logger.error(
            f"[{severity}] {exc_type.__name__}: {exc_val}\n{tb_text}"
        )

        if self._show_dialog:
            self._show_error_dialog(
                user_message=user_message,
                details=tb_text,
                is_critical=is_critical,
            )

        if is_critical and self._exit_on_critical:
            self._logger.critical("Critical error occurred.")
            if self._app is not None:
                self._app.exit(0x1)
            else:
                sys.exit(0x1)

    @staticmethod
    def _is_critical(exc_type: Type[BaseException]) -> bool:

        critical_types = (
            MemoryError,
            SystemError,
            RecursionError,
            ImportError,
        )
        return issubclass(exc_type, critical_types)

    def _get_user_message(self, exc_type: Type[BaseException], exc_val: BaseException) -> str:
        for err_type in self._HANDLEABLE_ERRORS:
            if issubclass(exc_type, err_type):
                return f"{err_type.__name__}: {exc_val}"

        return f"Unexpected exception/error occurred: {exc_val}"

    @staticmethod
    def _show_error_dialog(user_message: str, details: str, is_critical: bool) -> None:
        if is_critical:
            icon = QMessageBox.Icon.Critical
            title = "Критическая ошибка"
        else:
            icon = QMessageBox.Icon.Warning
            title = "Ошибка"

        dialog = QMessageBox()
        dialog.setIcon(icon)
        dialog.setWindowTitle(title)
        dialog.setText(user_message)
        dialog.setDetailedText(details)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)

        dialog.exec()

    def log_warning(self, message: str) -> None:
        self._logger.warning(message)

    def log_info(self, message: str) -> None:
        self._logger.info(message)

    def safe_call(self, func, *args, **kwargs) -> Optional[Callable]:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self._handle_exception(e.__class__.__name__, e, e.__traceback__)
            return None