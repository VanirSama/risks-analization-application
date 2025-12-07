import winreg, os, sys, shutil
from pathlib import Path


def getIconPath():
    if getattr(sys, 'frozen', False):
        persistentIconDir = os.path.join(os.getenv('APPDATA'), 'AURA', 'icons')
        os.makedirs(persistentIconDir, exist_ok=True)
        persistentIconPath = os.path.join(persistentIconDir, 'icon_32.ico')

        tempIconPath = os.path.join(sys._MEIPASS, 'assets', 'icon_32.ico')
        if not os.path.exists(persistentIconPath):
            shutil.copyfile(tempIconPath, persistentIconPath)
        return persistentIconPath
    else:
        return os.path.join(Path(__file__).parent.parent, 'assets', 'icon_32.ico')

def associateRskExtension(appPath: str):
    iconPath = getIconPath()
    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, '.rsk') as key:
            winreg.SetValue(key, '', winreg.REG_SZ, 'AURA.RiskMap')

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 'AURA.RiskMap') as key:
            winreg.SetValue(key, '', winreg.REG_SZ, 'AURA Risk Map File')

            with winreg.CreateKey(key, 'DefaultIcon') as iconKey:
                winreg.SetValue(iconKey, '', winreg.REG_SZ, iconPath)

            with winreg.CreateKey(key, 'shell\\open\\command') as cmdKey:
                winreg.SetValue(cmdKey, '', winreg.REG_SZ, f'"{appPath}" "%1"')

        return True
    except Exception:
        return False


def isRskAssociated(appPath: str):
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, '.rsk') as key:
            fileType = winreg.QueryValue(key, '')
            if fileType != 'AURA.RiskMap':
                return False

        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, f'AURA.RiskMap\\shell\\open\\command') as key:
            currentCmd = winreg.QueryValue(key, '')
            return appPath in currentCmd
    except:
        return False
