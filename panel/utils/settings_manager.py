import json
import os
import platform
from language_enum import LANG_ENUM


class SettingsEnum():
    HOUDINI_PATH = "HOUDINI_PATH"
    LANGUAGE = "LANGUAGE"
    RECENT = "RECENT"


LANG_MAP = {
    LANG_ENUM.EN_US: ("en_us", 0),
    LANG_ENUM.ZH_CN: ("zh_cn", 1)
}

MAX_RECENT = 8

def getSettingsLanguageKeyIndex(lang_idx):
    if lang_idx in LANG_MAP:
        return LANG_MAP[lang_idx]
    return LANG_MAP[LANG_ENUM.ZH_CN]


class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._settings = {
                SettingsEnum.HOUDINI_PATH: "",
                SettingsEnum.LANGUAGE: "zh_cn",
                SettingsEnum.RECENT: []
            }
            cls._instance._file_path = cls._instance._getSettingsFilePath()
            cls._instance.loadSettings()
        return cls._instance

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

