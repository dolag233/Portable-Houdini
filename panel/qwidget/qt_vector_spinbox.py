import sys
from PySide2.QtWidgets import QWidget, QHBoxLayout, QDoubleSpinBox, QSpinBox, QApplication
from PySide2.QtCore import Signal

class QFloatVectorSpinBox(QWidget):
    valueChanged = Signal(list)

    def __init__(self, vector_length=3, parent=None):
        super(QFloatVectorSpinBox, self).__init__(parent)
        self.vector_length = vector_length
        self.spinboxes = []

        layout = QHBoxLayout()
        for _ in range(vector_length):
            spinbox = QDoubleSpinBox()
            spinbox.setRange(-1e6, 1e6)
            spinbox.setDecimals(3)
            spinbox.valueChanged.connect(self.emitValueChanged)
            layout.addWidget(spinbox)
            self.spinboxes.append(spinbox)

        self.setLayout(layout)

    def emitValueChanged(self):
        self.valueChanged.emit(self.value())

    def value(self):
        return [spinbox.value() for spinbox in self.spinboxes]

    def setRange(self, min_value, max_value):
        for spinbox in self.spinboxes:
            spinbox.setRange(min_value, max_value)

    def setValue(self, values):
        if len(values) != self.vector_length:
            raise ValueError(f"Expected {self.vector_length} values, got {len(values)}")
        for spinbox, value in zip(self.spinboxes, values):
            spinbox.setValue(value)

class QIntVectorSpinBox(QWidget):
    valueChanged = Signal(list)

    def __init__(self, vector_length=3, parent=None):
        super(QIntVectorSpinBox, self).__init__(parent)
        self.vector_length = vector_length
        self.spinboxes = []

        layout = QHBoxLayout()
        for _ in range(vector_length):
            spinbox = QSpinBox()
            spinbox.setRange(-1e6, 1e6)
            spinbox.valueChanged.connect(self.emitValueChanged)
            layout.addWidget(spinbox)
            self.spinboxes.append(spinbox)

        self.setLayout(layout)

    def emitValueChanged(self):
        self.valueChanged.emit(self.value())

    def value(self):
        return [spinbox.value() for spinbox in self.spinboxes]

    def setRange(self, min_value, max_value):
        for spinbox in self.spinboxes:
            spinbox.setRange(min_value, max_value)

    def setValue(self, values):
        if len(values) != self.vector_length:
            raise ValueError(f"Expected {self.vector_length} values, got {len(values)}")
        for spinbox, value in zip(self.spinboxes, values):
            spinbox.setValue(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 测试 QFloatVectorSpinBox
    float_vector_widget = QFloatVectorSpinBox(vector_length=4)
    float_vector_widget.setRange(-10.0, 10.0)
    float_vector_widget.setValue([1.1, 2.2, 3.3, 4.4])
    float_vector_widget.valueChanged.connect(lambda val: print("Float Vector Value Changed:", val))
    float_vector_widget.show()

    # 测试 QIntVectorSpinBox
    int_vector_widget = QIntVectorSpinBox(vector_length=4)
    int_vector_widget.setRange(-100, 100)
    int_vector_widget.setValue([10, 20, 30, 40])
    int_vector_widget.valueChanged.connect(lambda val: print("Int Vector Value Changed:", val))
    int_vector_widget.show()

    sys.exit(app.exec_())
