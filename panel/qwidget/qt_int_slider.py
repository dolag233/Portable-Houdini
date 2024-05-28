import sys
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpinBox, QSlider, QPushButton, QApplication
from PySide2.QtCore import Qt, Signal

class QIntegerSlider(QWidget):
    valueChanged = Signal(int)
    sliderReleased = Signal(int)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(QIntegerSlider, self).__init__(parent)

        self._min = 0
        self._max = 100

        # 创建 QSpinBox 和 QSlider
        self.spinbox = QSpinBox()
        self.slider = QSlider(orientation)

        # 设置 QSpinBox 的范围
        self.spinbox.setRange(self._min, self._max)
        self.spinbox.valueChanged.connect(self._onSpinboxValueChanged)

        # 设置 QSlider 的范围
        self.slider.setRange(self._min, self._max)
        self.slider.valueChanged.connect(self._onSliderValueChanged)
        self.slider.sliderReleased.connect(self._onSliderReleased)

        # 布局
        layout = QHBoxLayout()
        layout.addWidget(self.spinbox)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def setRange(self, min_value, max_value):
        self._min = min_value
        self._max = max_value
        self.spinbox.setRange(min_value, max_value)
        self.slider.setRange(min_value, max_value)

    def value(self):
        return self.spinbox.value()

    def setValue(self, value):
        self.spinbox.setValue(value)
        self.slider.setValue(value)

    def _onSpinboxValueChanged(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(value)
        self.slider.blockSignals(False)
        self.valueChanged.emit(value)

    def _onSliderValueChanged(self, value):
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(value)
        self.spinbox.blockSignals(False)
        self.valueChanged.emit(value)

    def _onSliderReleased(self):
        self.sliderReleased.emit(self.value())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    # 创建 QIntegerSlider 并添加到窗口中
    int_slider = QIntegerSlider()
    int_slider.setRange(0, 100)
    layout.addWidget(int_slider)

    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())
