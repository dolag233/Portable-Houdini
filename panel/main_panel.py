import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(current_dir, "utils"))
sys.path.append(os.path.join(current_dir, "qwidget"))
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter
from PySide2.QtCore import Qt
from menu_file import FileMenu
from menu_settings import SettingsMenu
from menu_window import WindowMenu
from hda_panel import HDAPanel
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from hou_parms_model import HouParmsModel
from hda_controller import HDAController
from utils.globals import SETTINGS_MANAGER, SettingsEnum
from panel.qwidget.qt_mesh_viewer import QMeshViewerPanel, QMeshViewer


class MainWindow(QMainWindow):
    _model = None
    _controller = None

    def __init__(self, model, controller):
        super().__init__()
        self._model = model
        self._controller = controller
        self.initUI()

    def initUI(self):
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_APP_TITLE))

        # Menu bar
        menubar = self.menuBar()

        file_menu = FileMenu(self)
        file_menu.load_hda.connect(self.updateHDA)
        file_menu.save_hip.connect(self.saveHIP)
        menubar.addMenu(file_menu)

        settings_menu = SettingsMenu(self)
        menubar.addMenu(settings_menu)

        window_menu = WindowMenu(self)
        menubar.addMenu(window_menu)
        window_menu.open_mesh_viewer.connect(self.onOpenMeshViewer)

        # Main widget
        self.main_widget = QWidget()
        main_widget_layout = QHBoxLayout()
        hda_mesh_splitter = QSplitter()
        self.hda_panel = HDAPanel(self._model, self._controller)
        self.mesh_viewer_panel = QMeshViewerPanel()
        self.mesh_viewer_panel.set_auto_update_model.connect(self.setAutoUpdateModel)
        self.mesh_viewer_panel.hide()
        hda_mesh_splitter.addWidget(self.hda_panel)
        hda_mesh_splitter.addWidget(self.mesh_viewer_panel)
        main_widget_layout.addWidget(hda_mesh_splitter)
        self.main_widget.setLayout(main_widget_layout)
        self.setCentralWidget(self.main_widget)

        # 打开上一次打开的hda
        if len(SETTINGS_MANAGER.get(SettingsEnum.RECENT)) > 0:
            file_menu.openRecentFile(SETTINGS_MANAGER.get(SettingsEnum.RECENT)[0])

    def updateHDA(self, hda_path, hda_name):
        if self._controller is not None and self._model is not None:
            try:
                import panel.utils.init_houdini
            except ImportError:
                return

            # clear
            self._controller.clearHDA()
            self._model.clearHDA()
            self.hda_panel.clearLayout(self.hda_panel.layout)

            self._controller.setCurHDAPath(hda_path)
            self._controller.setCurHDAName(hda_name)
            self._controller.loadHDA()
            self.hda_panel.setHDAName(hda_name)
            self.hda_panel.updateUI()
            self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_APP_TITLE) + " - " + hda_name)

    def saveHIP(self, hda_path):
        self._controller.saveHIP(hda_path)

    def setAutoUpdateModel(self, auto):
        self._controller.setAutoUpdateModel(auto)

    def onOpenMeshViewer(self):
        if self.mesh_viewer_panel.isHidden():
            self._controller.setAutoUpdateModel(True)
            self._controller.update_display_model.connect(self.mesh_viewer_panel.mesh_viewer.updateModel, Qt.DirectConnection)
            self._controller.updateNodeModel()
            self.mesh_viewer_panel.mesh_viewer.autoMoveCamera()
            self.mesh_viewer_panel.show()
        elif self.mesh_viewer_panel.isVisible():
            self._controller.setAutoUpdateModel(False)
            self._controller.update_display_model.disconnect()
            self.mesh_viewer_panel.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = HouParmsModel()
    controller = HDAController(model)
    window = MainWindow(model, controller)
    window.show()
    sys.exit(app.exec_())
