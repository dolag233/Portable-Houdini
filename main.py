import sys
import os

# config path and qt platform
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "panel"))
qt_plugin_path = os.path.join(os.path.dirname(sys.executable), r"Lib\site-packages\PySide2\plugins")
os.environ["path"] += os.path.join(qt_plugin_path, "platforms")
os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

# load qt style
from panel.utils import globals
from PySide2.QtWidgets import QApplication, QMessageBox
from PySide2.QtGui import QIcon
from panel.utils.theme import Theme
theme = Theme()
app = QApplication(sys.argv)
from panel.main_panel import MainWindow
from panel.hou_parms_model import HouParmsModel
from panel.remote_hda_controller import RemoteHDAController
from panel.utils.settings_manager import SettingsEnum, SettingsManager
from panel.utils.localization import LANG_STR_ENUM, getLocalizationStr
from PySide2.QtCore import QThread
globals.APP = app

if __name__ == '__main__':
    # 设置主题
    theme.setTheme()
    
    # 注意：客户端完全不支持本地 Houdini，仅支持远程连接
    # 移除了 Houdini 路径检查和错误弹窗
    
    model = HouParmsModel()
    # 使用远程控制器，仅支持远程模式
    controller = RemoteHDAController(model)
    controller.set_mode("remote")  # 仅支持远程模式
    
    window = MainWindow(model, controller)
    globals.MAIN_WINDOW = window
    window.setWindowIcon(QIcon("icon.png"))
    window.show()
    sys.exit(app.exec_())