import sys
from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar, QLabel

class QProgressBarWidget(QWidget):
    def __init__(self, total_time, update_interval=10, parent=None):
        super().__init__(parent)
        self.total_time = total_time
        self.current_time = 0
        self.update_interval = update_interval

        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置窗口无边框

        self.layout = QVBoxLayout()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(self.total_time * 1000 // self.update_interval)  # 进度条的最大值基于更新间隔
        self.layout.addWidget(self.progress_bar)

        self.label = QLabel(f"Time: 0s / {self.total_time}s", self)
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(self.update_interval)  # 每0.05秒更新一次

    def updateProgress(self):
        self.current_time += self.update_interval / 1000
        self.progress_bar.setValue(self.current_time * 1000 // self.update_interval)
        self.label.setText(f"Time: {self.current_time:.2f}s / {self.total_time}s")

        if self.current_time >= self.total_time:
            self.timer.stop()

    def setUpdateInterval(self, interval):
        self.update_interval = interval
        self.timer.setInterval(self.update_interval)
        self.progress_bar.setMaximum(self.total_time * 1000 // self.update_interval)

if __name__ == '__main__':
    app = QApplication([])
    total_time = 10
    progress_bar = QProgressBarWidget(total_time)
    progress_bar.show()
    sys.exit(app.exec_())
