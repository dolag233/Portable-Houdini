import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(current_dir, "utils"))
sys.path.append(os.path.join(current_dir, "qwidget"))
from PySide2.QtWidgets import QApplication, QMainWindow
from menu_file import FileMenu
from menu_settings import SettingsMenu
from hda_panel import HDAPanel
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from hou_parms_model import HouParmsModel
from hda_controller import HDAController
from utils.globals import SETTINGS_MANAGER, SettingsEnum


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
        menubar.addMenu(file_menu)

        settings_menu = SettingsMenu(self)
        menubar.addMenu(settings_menu)

        # Main widget
        self.hda_panel = HDAPanel(self._model)
        self.setCentralWidget(self.hda_panel)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = HouParmsModel()
    controller = HDAController(model)
    window = MainWindow(model, controller)
    window.show()
    sys.exit(app.exec_())
