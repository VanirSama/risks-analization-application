from PySide6.QtGui import QFontDatabase


def load_fonts(app):
    font_path = app.resource_loader.get("STROGO_FONT", "")
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1: Fonts.STROGO = QFontDatabase.applicationFontFamilies(font_id)[0]


class Fonts:
   STROGO = ""