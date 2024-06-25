from PySide2.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from utils import globals
from utils.settings_manager import SettingsEnum
from utils.globals import SETTINGS_MANAGER, LANG_ENUM, LangEnumToStr, LangStrToEnum

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_GENERAL))
        self.initUI()

    def initUI(self):
        layout = QFormLayout()

        self.houdini_path = QLineEdit()
        self.houdini_path.setText(SETTINGS_MANAGER.get(SettingsEnum.HOUDINI_PATH))
        layout.addRow(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_HOUDINI_ROOT), self.houdini_path)

        self.language = QComboBox()
        self.language.addItems([getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_EN_US),
                                getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE_ZH_CN)])
        self.language.setCurrentIndex(LangStrToEnum(SETTINGS_MANAGER.get(SettingsEnum.LANGUAGE)))

        layout.addRow(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_LANGUAGE), self.language)

        self.theme = QComboBox()
        self.theme.addItems(["auto", "dark", "light"])
        self.theme.setCurrentText(SETTINGS_MANAGER.get(SettingsEnum.THEME))
        layout.addWidget(self.theme)

        self.save_button = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_SAVE))
        self.save_button.clicked.connect(self.saveSettings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def saveSettings(self):
        SETTINGS_MANAGER.set(SettingsEnum.HOUDINI_PATH, self.houdini_path.text())
        SETTINGS_MANAGER.set(SettingsEnum.LANGUAGE, LangEnumToStr(self.language.currentIndex()))
        SETTINGS_MANAGER.set(SettingsEnum.THEME, self.theme.currentText())
        SETTINGS_MANAGER.saveSettings()
        HOUDINI_PATH = SETTINGS_MANAGER.get(SettingsEnum.HOUDINI_PATH)
        try:
            import utils.init_houdini
        except ImportError:
            return
        self.flushSettings()
        self.close()

    def flushSettings(self):
        #globals.LANGUAGE = LANG_ENUM.strToEnum(SETTINGS_MANAGER.get(SettingsEnum.LANGUAGE))
        from panel.utils.theme import Theme
        Theme().setTheme()

