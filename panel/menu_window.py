import os

from PySide2.QtWidgets import QMenu, QAction, QFileDialog
from PySide2.QtCore import Signal
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from utils.globals import SETTINGS_MANAGER, SettingsEnum
from functools import partial


class WindowMenu(QMenu):
    open_mesh_viewer = Signal()

    def __init__(self, parent=None):
        super().__init__(getLocalizationStr(LANG_STR_ENUM.UI_MENU_WINDOW), parent)
        self.initUI()

    def initUI(self):
        open_mew_viewer_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_MENU_WINDOW_MESH_VIEWER), self)
        open_mew_viewer_action.triggered.connect(self.open_mesh_viewer.emit)
        self.addAction(open_mew_viewer_action)
