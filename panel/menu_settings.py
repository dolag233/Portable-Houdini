from PySide2.QtWidgets import QMenu, QAction
from menu_settings_dialog import SettingsDialog
from utils.localization import LANG_STR_ENUM, getLocalizationStr


class SettingsMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS), parent)
        self.initUI()

    def initUI(self):
        deep_settings_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_MENU_SETTINGS_GENERAL), self)
        self.addAction(deep_settings_action)

        # Connect the deep settings action
        deep_settings_action.triggered.connect(self.open_settings_dialog)

    def open_settings_dialog(self):
        dialog = SettingsDialog()
        dialog.exec_()
