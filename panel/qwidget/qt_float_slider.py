import sys
from PySide2.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QDoubleSpinBox, QSlider, QPushButton, QApplication
from PySide2.QtCore import Qt, Signal

class QFloatSlider(QWidget):
    floatValueChanged = Signal(float)
    floatSliderReleased = Signal(float)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super(QFloatSlider, self).__init__(parent)

        self._min = 0.0
        self._max = 1.0

        # 创建 QDoubleSpinBox 和 QSlider
        self.spinbox = QDoubleSpinBox()
        self.slider = QSlider(orientation)

        # 设置 QDoubleSpinBox 的范围和精度
        self.spinbox.setRange(self._min, self._max)
        self.spinbox.setDecimals(3)
        self.spinbox.valueChanged.connect(self._onSpinboxValueChanged)

        # 设置 QSlider 的范围
        self.slider.setRange(0, 1000)  # 这里设置为1000以确保滑块有足够的精度
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

    def value(self):
        return self.spinbox.value()

    def setValue(self, value):
        self.spinbox.setValue(value)
        self.slider.setValue(self._floatToInt(value))

    def _floatToInt(self, value):
        return int((value - self._min) / (self._max - self._min) * 1000)

    def _intToFloat(self, value):
        return self._min + (value / 1000.0) * (self._max - self._min)

    def _onSpinboxValueChanged(self, value):
        self.slider.blockSignals(True)
        self.slider.setValue(self._floatToInt(value))
        self.slider.blockSignals(False)
        self.floatValueChanged.emit(value)

    def _onSliderValueChanged(self, value):
        float_value = self._intToFloat(value)
        self.spinbox.blockSignals(True)
        self.spinbox.setValue(float_value)
        self.spinbox.blockSignals(False)
        self.floatValueChanged.emit(float_value)

    def _onSliderReleased(self):
        self.floatSliderReleased.emit(self.value())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)

    # 创建 QFloatSlider 并添加到窗口中
    float_slider = QFloatSlider()
    float_slider.setRange(0.0, 1.0)
    layout.addWidget(float_slider)

    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())
