from PySide2.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from utils import globals
from utils.settings_manager import SettingsManager, SettingsEnum, getSettingsLanguageKeyIndex
import os


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_GENERAL))
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        self.houdini_path = QLineEdit()
        self.houdini_path.setText(SettingsManager().get(SettingsEnum.HOUDINI_PATH))
        layout.addRow(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_HOUDINI_ROOT), self.houdini_path)

        self.language = QComboBox()
        self.language.addItems([getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_ZH_CN),
                                getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_EN_US)])
        self.language.setCurrentIndex(getSettingsLanguageKeyIndex(SettingsManager().get(SettingsEnum.LANGUAGE))[-1])

        layout.addRow(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE), self.language)
        self.save_button = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_SAVE))
        self.save_button.clicked.connect(self.saveSettings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def saveSettings(self):
        SettingsManager().set(SettingsEnum.HOUDINI_PATH, self.houdini_path.text())
        SettingsManager().set(SettingsEnum.LANGUAGE, getLocalizationStr(self.language.currentIndex()))
        SettingsManager().saveSettings()
        HOUDINI_PATH = SettingsManager().get(SettingsEnum.HOUDINI_PATH)
        print(HOUDINI_PATH)
        try:
            import utils.init_houdini
        except ImportError:
            return
        self.close()
