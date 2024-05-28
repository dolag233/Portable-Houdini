import sys
from PySide2.QtWidgets import QWidget, QHBoxLayout, QColorDialog, QSpinBox, QPushButton
from PySide2.QtCore import Signal
from PySide2.QtGui import QColor


class QColorSelector(QWidget):
    valueChanged = Signal(list)

    def __init__(self, use_alpha=False, parent=None):
        super(QColorSelector, self).__init__(parent)

        self.use_alpha = use_alpha
        self.color = QColor(0, 0, 0, 255) if use_alpha else QColor(0, 0, 0)

        # 创建颜色选择器按钮
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.openColorDialog)

        # 创建 RGB(A) 数值显示的 QSpinBox
        self.r_spinbox = QSpinBox()
        self.g_spinbox = QSpinBox()
        self.b_spinbox = QSpinBox()
        self.a_spinbox = QSpinBox() if use_alpha else None

        # 设置 QSpinBox 的范围
        for spinbox in (self.r_spinbox, self.g_spinbox, self.b_spinbox):
            spinbox.setRange(0, 255)
            spinbox.valueChanged.connect(self.updateColorFromSpinbox)

        if use_alpha:
            self.a_spinbox.setRange(0, 255)
            self.a_spinbox.valueChanged.connect(self.updateColorFromSpinbox)

        # 初始化 QSpinBox 的值
        self.updateSpinboxes()

        # 布局
        layout = QHBoxLayout()
        layout.addWidget(self.color_button)
        layout.addWidget(self.r_spinbox)
        layout.addWidget(self.g_spinbox)
        layout.addWidget(self.b_spinbox)
        if use_alpha:
            layout.addWidget(self.a_spinbox)

        self.setLayout(layout)

    def openColorDialog(self):
        color = QColorDialog.getColor(self.color, self, "Select Color")
        if color.isValid():
            self.color = color
            self.updateSpinboxes()
            self.emitValueChanged()

    def updateSpinboxes(self):
        self.r_spinbox.setValue(self.color.red())
        self.g_spinbox.setValue(self.color.green())
        self.b_spinbox.setValue(self.color.blue())
        if self.use_alpha:
            self.a_spinbox.setValue(self.color.alpha())

    def updateColorFromSpinbox(self):
        self.color.setRed(self.r_spinbox.value())
        self.color.setGreen(self.g_spinbox.value())
        self.color.setBlue(self.b_spinbox.value())
        if self.use_alpha:
            self.color.setAlpha(self.a_spinbox.value())
        self.updateButtonColor()
        self.emitValueChanged()

    def updateButtonColor(self):
        self.color_button.setStyleSheet(f"background-color: {self.color.name()}")

    def setValue(self, color):
        if isinstance(color, QColor):
            self.color = color
            self.updateSpinboxes()
            self.updateButtonColor()
            self.emitValueChanged()
        else:
            raise ValueError("setValue expects a QColor instance")

    def emitValueChanged(self):
        color_values = [self.color.red(), self.color.green(), self.color.blue()]
        if self.use_alpha:
            color_values.append(self.color.alpha())
        self.valueChanged.emit(color_values)

