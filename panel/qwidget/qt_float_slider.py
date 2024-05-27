from PySide2.QtWidgets import QSlider
from PySide2.QtCore import Qt, Signal

class QFloatSlider(QSlider):
    floatValueChanged = Signal(float)
    floatSliderReleased = Signal(float)

    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self._min = 0.0
        self._max = 1.0
        self._precision = 1000  # 控制精度

        self.valueChanged.connect(self._emit_float_value_changed)
        self.sliderReleased.connect(self._emit_float_slider_released)

    def setRange(self, min_value, max_value):
        self._min = min_value
        self._max = max_value
        super().setRange(0, self._precision)

    def value(self):
        int_value = super().value()
        return self._int_to_float(int_value)

    def setValue(self, value):
        int_value = self._float_to_int(value)
        super().setValue(int_value)

    def _float_to_int(self, value):
        return int((value - self._min) / (self._max - self._min) * self._precision)

    def _int_to_float(self, value):
        return self._min + (value / self._precision) * (self._max - self._min)

    def _emit_float_value_changed(self, value):
        float_value = self._int_to_float(value)
        self.floatValueChanged.emit(float_value)

    def _emit_float_slider_released(self):
        float_value = self.value()
        self.floatSliderReleased.emit(float_value)
