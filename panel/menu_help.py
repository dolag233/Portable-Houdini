from PySide2.QtWidgets import QMenu, QAction, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QApplication
from PySide2.QtCore import Qt
from menu_settings_dialog import SettingsDialog
from utils.localization import LANG_STR_ENUM, getLocalizationStr
import webbrowser
from utils.app_update import AppUpdate
from utils.globals import MAIN_WINDOW

class HelpMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP), parent)
        self.project_url = "https://github.com/dolag233/Portable-Houdini"
        self.repo_url = "dolag233/Portable-Houdini"
        self.initUI()

    def initUI(self):
        open_project_url_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP_PROJECT_URL), self)
        open_project_url_action.triggered.connect(self.openProjectURL)
        self.addAction(open_project_url_action)

        update_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP_UPDATE), self)
        update_action.triggered.connect(self.openUpdateWindow)
        self.addAction(update_action)

    def openProjectURL(self):
        webbrowser.open(self.project_url)

    def openUpdateWindow(self):
        self.update_window = UpdateWindow()
        self.update_window.show()

class UpdateWindow(QWidget):
    def __init__(self):
        super().__init__()
        print("update init")
        self.initUI()

        download_to = '.'  # 指定下载文件夹
        extract_to = download_to  # 指定解压缩文件夹
        ignore_list = ['app_update.py', 'venv', '.git', '.idea']  # 需要忽略的文件或文件夹

        self.updater = AppUpdate('dolag233/Portable-Houdini', download_to, extract_to, ignore_list)
        self.updater.update_complete.connect(self.on_update_complete)
        self.updater.update_failed.connect(self.on_update_failed)

    def initUI(self):
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP_UPDATE_TITLE))
        size = (250, 150)
        if MAIN_WINDOW is not None:
            self.setGeometry(MAIN_WINDOW.geometry().x(), MAIN_WINDOW.geometry().y(), size[0], size[1])
            print(MAIN_WINDOW.geometry().x())
        else:
            self.setGeometry(0, 0, size[0], size[1])

        layout = QVBoxLayout()

        self.info_label = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP_UPDATE_WARNING),
                                 self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("color: red; font-size: 14px;")
        layout.addWidget(self.info_label)

        self.update_button = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_MENU_HELP_UPDATE_BUTTON), self)
        self.update_button.clicked.connect(self.on_update_button_clicked)
        layout.addWidget(self.update_button)

        self.setLayout(layout)

    def on_update_button_clicked(self):
        self.updater.apply_update()

    def on_update_complete(self):
        QMessageBox.information(self, "更新完成", "工具已成功更新。")
        self.close()
        import sys
        sys.exit(0)

    def on_update_failed(self, message):
        QMessageBox.critical(self, "更新失败", message)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = UpdateWindow()
    window.show()
    sys.exit(app.exec_())
