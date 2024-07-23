import os

from PySide2.QtWidgets import QMenu, QAction, QFileDialog, QErrorMessage
from PySide2.QtCore import Signal
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from utils.globals import SETTINGS_MANAGER, SettingsEnum
from functools import partial
import tkinter as tk
from tkinter import filedialog
class FileMenu(QMenu):
    load_hda = Signal(str, str)  # path, name
    load_hip = Signal(str, str)  # path, name
    save_hip = Signal(str)  # path

    def __init__(self, parent=None):
        super().__init__(getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE), parent)
        self.initUI()

    def initUI(self):
        open_hda_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_HDA), self)
        open_hda_action.triggered.connect(self.openHdaFile)
        self.addAction(open_hda_action)

        open_hip_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_HIP), self)
        open_hip_action.triggered.connect(self.openHipFile)
        self.addAction(open_hip_action)

        self.recent_menu = QMenu(getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_RECENT), self)
        self.recent_menu.aboutToShow.connect(self.onHoverRencetFiles)
        self.addMenu(self.recent_menu)

        open_hip_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_SAVE_HIP), self)
        open_hip_action.triggered.connect(self.saveHipFile)
        self.addAction(open_hip_action)

    def openHdaFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_HDA_FILE_DIALOG_TITLE)
                                                   , "", "HDA Files (*.hda);;HDA Files (*.vtl);;All Files (*)")

        if file_path:
            file_name = file_path.split('\\')[-1]
            if len(file_name) == len(file_path):
                file_name = file_name.split('/')[-1]
            self.load_hda.emit(file_path, file_name)

            SETTINGS_MANAGER.appendRecentFiles(file_path)
            SETTINGS_MANAGER.saveSettings()

    def openHipFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_HIP_FILE_DIALOG_TITLE)
                                                   , "", "HIP Files (*.hip);;HIP Files (*.hipc);;All Files (*)")

        if file_path:
            file_name = file_path.split('\\')[-1]
            if len(file_name) == len(file_path):
                file_name = file_name.split('/')[-1]
            self.load_hda.emit(file_path, file_name)

    def saveHipFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_SAVE_HIP_FILE_DIALOG_TITLE)
                     , '', "HIP Files (*.hip);;HIP Files (*.hipc);;All Files (*)")

        if not os.path.exists(os.path.dirname(file_path)):
            msg_box = QErrorMessage()
            msg_box.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.ERROR_TITLE))
            msg_box.setText(getLocalizationStr(LANG_STR_ENUM.ERROR_INVALID_FILE_PATH))
            msg_box.show()

        else:
            self.save_hip.emit(file_path)


    def onHoverRencetFiles(self):
        self.recent_menu.clear()
        recents = SETTINGS_MANAGER.get(SettingsEnum.RECENT)
        for recent_file in recents:
            recent_file_action = QAction(recent_file, self)
            recent_file_action.triggered.connect(partial(self.openRecentFile, recent_file))
            self.recent_menu.addAction(recent_file_action)

    def openRecentFile(self, file_path):
        if isinstance(file_path, str) and os.path.isfile(file_path):
            file_name = file_path.split('\\')[-1]
            if len(file_name) == len(file_path):
                file_name = file_name.split('/')[-1]
            if ".hda" in file_path:
                self.load_hda.emit(file_path, file_name)
            elif ".hip" in file_path:
                self.load_hip.emit(file_path, file_name)

            SETTINGS_MANAGER.appendRecentFiles(file_path)
            SETTINGS_MANAGER.saveSettings()

            