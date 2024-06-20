from language_enum import LANG_ENUM

from settings_manager import SettingsManager, SettingsEnum
SETTINGS_MANAGER = SettingsManager()

LANGUAGE = LANG_ENUM.ZH_CN

APP = None

def setLanguage(language_idx):
    global LANGUAGE
    if language_idx == 0:
        LANGUAGE = LANG_ENUM.ZH_CN
    elif language_idx == 1:
        LANGUAGE = LANG_ENUM.EN_US
