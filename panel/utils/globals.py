"""
    Load globals before any widget
"""

from panel.utils.language_enum import *
from panel.utils.settings_manager import SettingsManager, SettingsEnum

SETTINGS_MANAGER = SettingsManager()

LANGUAGE = LangStrToEnum(SETTINGS_MANAGER.get(SettingsEnum.LANGUAGE))

APP = None
