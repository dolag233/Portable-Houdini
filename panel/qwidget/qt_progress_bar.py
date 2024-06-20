import sys
from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel
from utils.localization import getLocalizationStr, LANG_STR_ENUM

class QProgressBarWidget(QWidget):
    def __init__(self, parent=None, update_interval=50):
        super().__init__(parent)
        self.current_time = 0
        self.update_interval = update_interval

        self.initUI()

    def initUI(self):
        #self.setWindowFlags(Qt.FramelessWindowHint)  # 设置窗口无边框
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_COOK_TITLE))
        self.layout = QVBoxLayout()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # 使进度条保持加载状态
        self.layout.addWidget(self.progress_bar)

        self.label = QLabel("{}0.00s".format(getLocalizationStr(LANG_STR_ENUM.UI_COOK_TIME_LABEL)), self)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(self.update_interval)  # 每0.05秒更新一次

    def refreshTime(self):
        self.current_time = 0

    def updateProgress(self):
        self.current_time += self.update_interval / 1000
        time_str = getLocalizationStr(LANG_STR_ENUM.UI_COOK_TIME_LABEL)
        self.label.setText(f"{time_str}{self.current_time:.2f}s")

    def setUpdateInterval(self, interval):
        self.update_interval = interval
        self.timer.setInterval(self.update_interval)

if __name__ == '__main__':
    app = QApplication([])
    progress_bar = QProgressBarWidget()
    progress_bar.show()
    sys.exit(app.exec_())
