import os

from PySide2.QtWidgets import QMenu, QAction, QFileDialog
from PySide2.QtCore import Signal
from utils.localization import LANG_STR_ENUM, getLocalizationStr


class FileMenu(QMenu):
    load_hda = Signal(str, str)  # path, name
    load_hip = Signal(str, str)  # path, name

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

        open_recent_menu = QMenu(getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_RECENT), self)
        self.addMenu(open_recent_menu)

    def openHdaFile(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_HDA_FILE_DIALOG_TITLE)
                                                   , "", "HDA Files (*.hda);;HDA Files (*.vtl);;All Files (*)", options=options)
        if file_path:
            file_name = file_path.split('\\')[-1]
            if len(file_name) == len(file_path):
                file_name = file_name.split('/')[-1]
            self.load_hda.emit(file_path, file_name)

    def openHipFile(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, getLocalizationStr(LANG_STR_ENUM.UI_MENU_FILE_OPEN_HIP_FILE_DIALOG_TITLE)
                                                   , "", "HIP Files (*.hip);;HIP Files (*.hipc);;All Files (*)", options=options)
        if file_path:
            file_name = file_path.split('\\')[-1]
            if len(file_name) == len(file_path):
                file_name = file_name.split('/')[-1]
            self.load_hda.emit(file_path, file_name)
