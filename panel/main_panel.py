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
        self.setUITheme()

    def setUITheme(self):
        self.setStyleSheet("""
                    QWidget {
                        background-color: #2b2b2b;
                        color: #f0f0f0;
                        font-size: 14px;
                    }
                    QTextEdit, QLineEdit {
                        background-color: #3c3c3c;
                        border: 1px solid #555555;
                        color: #ffffff;
                    }
                    QPushButton {
                        background-color: #5c5c5c;
                        border: 1px solid #707070;
                        color: #ffffff;
                        padding: 5px;
                        min-width: 60px;
                    }
                    QPushButton:hover {
                        background-color: #6c6c6c;
                    }
                    QPushButton:pressed {
                        background-color: #4c4c4c;
                    }
                    QComboBox {
                        background-color: #3c3c3c;
                        border: 1px solid #555555;
                        color: #ffffff;
                        padding: 5px;
                        min-width: 80px;
                    }
                    QComboBox::drop-down {
                        border: 0px;
                    }
                    QComboBox::down-arrow {
                        image: url(noimg.png);  /* Placeholder, ensure to replace with a valid image */
                        width: 10px;
                        height: 10px;
                    }
                    QComboBox QAbstractItemView {
                        background-color: #3c3c3c;
                        border: 1px solid #555555;
                        color: #ffffff;
                        selection-background-color: #5c5c5c;
                    }
                """)

    def updateHDA(self, hda_path, hda_name):
        if self._controller is not None:
            self._controller.setCurHDAPath(hda_path)
            self._controller.setCurHDAName(hda_name)
            self._controller.loadHDA()

            self.hda_panel.updateUI()
            self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_APP_TITLE) + " - " + hda_name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = HouParmsModel()
    controller = HDAController(model)
    window = MainWindow(model, controller)
    window.show()
    sys.exit(app.exec_())
