import json
import os
import platform
from panel.utils.language_enum import *


class SettingsEnum:
    HOUDINI_PATH = "HOUDINI_PATH"
    LANGUAGE = "LANGUAGE"
    RECENT = "RECENT"
    THEME = "THEME"


MAX_RECENT = 8


class SingletonMeta(type):
    """
    A metaclass that creates a Singleton base type when called.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SettingsManager(metaclass=SingletonMeta):
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._settings = {
                SettingsEnum.HOUDINI_PATH: "",
                SettingsEnum.LANGUAGE: LangEnumToStr(LANG_ENUM.EN_US),
                SettingsEnum.RECENT: [],
                SettingsEnum.THEME: "auto"
            }
            self._file_path = self._getSettingsFilePath()
            self.loadSettings()
            self._initialized = True

    def _getSettingsFilePath(self):
        system = platform.system()
        if system == 'Windows':
            appdata_dir = os.getenv('APPDATA')
            settings_dir = os.path.join(appdata_dir, "Portable Houdini")
        else:
            home_dir = os.path.expanduser('~')
            settings_dir = os.path.join(home_dir, ".config", "Portable Houdini")

        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        return os.path.join(settings_dir, "Settings.json")

    def loadSettings(self):
        if os.path.exists(self._file_path):
            with open(self._file_path, 'r') as f:
                self._settings.update(json.load(f))

    def saveSettings(self):
        with open(self._file_path, 'w') as f:
            json.dump(self._settings, f, indent=4)

    # temp
    def appendRecentFiles(self, file_path):
        if file_path in self._settings[SettingsEnum.RECENT]:
            self._settings[SettingsEnum.RECENT].remove(file_path)

        self._settings[SettingsEnum.RECENT] = [file_path] + self._settings[SettingsEnum.RECENT][:MAX_RECENT]

    def get(self, key):
        return self._settings[key]

    def set(self, key, value):
        self._settings[key] = value

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)
