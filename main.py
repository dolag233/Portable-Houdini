import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "panel"))
from PySide2.QtWidgets import QApplication, QMessageBox
app = QApplication(sys.argv)
from panel.main_panel import MainWindow
from panel.hou_parms_model import HouParmsModel
from panel.hda_controller import HDAController
from panel.utils.settings_manager import SettingsEnum, SettingsManager
from panel.utils.localization import LANG_STR_ENUM, getLocalizationStr

settings = SettingsManager()
settings.loadSettings()

if __name__ == '__main__':
    # check if houdini_path is valid
    if not os.path.isdir(settings.get(SettingsEnum.HOUDINI_PATH)):
        msg_box = QMessageBox(QMessageBox.Warning, getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH), getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH_SETTINGS))
        msg_box.exec_()

    model = HouParmsModel()
    controller = HDAController(model)
    window = MainWindow(model, controller)
    window.show()
    sys.exit(app.exec_())