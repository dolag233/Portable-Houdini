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
# stylesheet = load_stylesheet(qtvsc.Theme.LIGHT_VS)
additional_qss = """
QToolTip {
    color: silver; /* 字体颜色 */
    background-color: #08101F; /* 背景颜色 */
    border: 1px solid white;
}
"""
qdarktheme.setup_theme("auto", additional_qss=additional_qss)

from panel.main_panel import MainWindow
from panel.hou_parms_model import HouParmsModel
from panel.hda_controller import HDAController
from panel.utils.settings_manager import SettingsEnum, SettingsManager
from panel.utils.localization import LANG_STR_ENUM, getLocalizationStr
from panel.utils import globals
from PySide2.QtCore import QThread
globals.APP = app

if __name__ == '__main__':
    # check if houdini_path is valid
    globals.SETTINGS_MANAGER.loadSettings()
    if not os.path.isdir(globals.SETTINGS_MANAGER.get(SettingsEnum.HOUDINI_PATH)):
        msg_box = QMessageBox(QMessageBox.Warning, getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH), getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH_SETTINGS))
        msg_box.exec_()

    model = HouParmsModel()
    houdini_thread = QThread()
    controller = HDAController(model)
    controller.moveToThread(houdini_thread)  # 现在controller处在单独线程，不会阻塞UI主线程
    houdini_thread.start()
    window = MainWindow(model, controller)
    window.setWindowIcon(QIcon("icon.png"))
    window.show()
    sys.exit(app.exec_())