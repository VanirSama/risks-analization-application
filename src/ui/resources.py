import os
import sys
from pathlib import Path


class ResourceLoader:
    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self.baseDir = sys._MEIPASS
        else:
            self.baseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def absPath(self, relativePath: str, ignoreMEIPASS:bool=False) -> str:
        if not ignoreMEIPASS:
            return os.path.join(self.baseDir, relativePath) if relativePath else ""
        else:
            return os.path.join(str(Path(sys.executable).parent)) if relativePath else ""


rl: ResourceLoader = ResourceLoader()
SPLASH_SCREEN_LOGO = rl.absPath("./assets/logo.png")
DOCUMENT_ICON_LOGO = rl.absPath("./assets/icon.png")
RECENT_FILES_JSON = rl.absPath("./recent_files.json")
APP_ICON = rl.absPath("./assets/icon_app.png")
TEMPLATES_FOLDER = rl.absPath("./templates")
