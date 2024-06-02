import sys
import os

# config path and qt platform
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "panel"))
qt_plugin_path = os.path.join(os.path.dirname(sys.executable), r"Lib\site-packages\PySide2\plugins")
os.environ["path"] += os.path.join(qt_plugin_path, "platforms")
os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

# load qt style
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtGui import QIcon
import qdarktheme
qdarktheme.enable_hi_dpi()
app = QApplication(sys.argv)
app.setWindowIcon(QIcon('icon.png'))
# stylesheet = load_stylesheet(qtvsc.Theme.LIGHT_VS)
qdarktheme.setup_theme("auto")

from panel.main_panel import MainWindow
from panel.hou_parms_model import HouParmsModel
from panel.hda_controller import HDAController
from panel.utils.settings_manager import SettingsEnum, SettingsManager
from panel.utils.localization import LANG_STR_ENUM, getLocalizationStr
from panel.utils.globals import SETTINGS_MANAGER

if __name__ == '__main__':
    # check if houdini_path is valid
    SETTINGS_MANAGER.loadSettings()
    if not os.path.isdir(SETTINGS_MANAGER.get(SettingsEnum.HOUDINI_PATH)):
        msg_box = QMessageBox(QMessageBox.Warning, getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH), getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH_SETTINGS))
        msg_box.exec_()

    model = HouParmsModel()
    controller = HDAController(model)
    window = MainWindow(model, controller)
    window.show()
    sys.exit(app.exec_())