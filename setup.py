import sys, os
from cx_Freeze import setup, Executable

PYQT5_DIR = "C:\Python34\Lib\site-packages\PyQt5"

include_files = [
    (os.path.join(PYQT5_DIR, "qml", "QtQuick.2"), "QtQuick.2"),
    (os.path.join(PYQT5_DIR, "qml", "QtQuick"), "QtQuick"),
    (os.path.join(PYQT5_DIR, "qml", "QtGraphicalEffects"), "QtGraphicalEffects"),
    "LauncherUI/",
    "GameUI/",
    #"Music/",
    #"Images/",
    ]
packages = []

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'



options = {
    'build_exe': {
        'includes': ['atexit', "server", "client", "game", "ServerControl"],
        "include_files": include_files,
        "packages": packages,
    }
}

executables = [
    Executable('Application.py', base=base)
]

setup(name='Paranoia',
      version='0.6',
      description='E-Board game over LAN',
      options=options,
      executables=executables
      )