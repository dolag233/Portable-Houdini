import sys
from PySide2.QtWidgets import QWidget, QHBoxLayout, QColorDialog, QSpinBox, QLabel, QPushButton
from PySide2.QtCore import Signal
from PySide2.QtGui import QColor


class QColorSelector(QWidget):
    valueChanged = Signal(list)
    valueChanged01 = Signal(list)

    def __init__(self, use_alpha=False, use_color01=True, parent=None):
        super(QColorSelector, self).__init__(parent)

        self.use_alpha = use_alpha
        self.use_color01 = use_color01
        self.color = QColor(255, 255, 255, 255) if use_alpha else QColor(255, 255, 255)

        # 创建颜色选择器按钮
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 20)
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
        self.updateColor()
        layout.addWidget(self.r_spinbox)
        layout.addWidget(self.g_spinbox)
        layout.addWidget(self.b_spinbox)
        if use_alpha:
            layout.addWidget(self.a_spinbox)

        self.setLayout(layout)

    def updateColor(self):
        color_name = self.color.name()
        # 设置按钮样式表
        self.color_button.setStyleSheet('background-color: {}; color: white; font-size: 16px;'.format(color_name))

    def openColorDialog(self):
        color = QColorDialog.getColor(self.color, self, "Select Color")
        if color.isValid():
            self.color = color
            self.updateSpinboxes()
            self.updateColor()
            self.emitValueChanged()

    def updateSpinboxes(self):
        color = self.color.getRgb()
        self.r_spinbox.setValue(color[0])
        self.g_spinbox.setValue(color[1])
        self.b_spinbox.setValue(color[2])
        if self.use_alpha:
            self.a_spinbox.setValue(color[3])

    def updateColorFromSpinbox(self):
        self.color.setRed(self.r_spinbox.value())
        self.color.setGreen(self.g_spinbox.value())
        self.color.setBlue(self.b_spinbox.value())
        if self.use_alpha:
            self.color.setAlpha(self.a_spinbox.value())
        self.updateColor()
        if self.use_color01:
            self.emitValueChanged01()
        else:
            self.emitValueChanged()

    def value(self):
        return list(self.color.getRgbF())

    def setValue(self, color):
        if self.use_color01:
            color = [x * 255 for x in color]

        self.color = QColor(*color)
        self.updateSpinboxes()
        self.updateColor()
        if self.use_color01:
            self.emitValueChanged01()
        else:
            self.emitValueChanged()

    def emitValueChanged(self):
        color_values = [self.color.red(), self.color.green(), self.color.blue()]
        if self.use_alpha:
            color_values.append(self.color.alpha())
        self.valueChanged.emit(color_values)

    def emitValueChanged01(self):
        color_values = [self.color.red(), self.color.green(), self.color.blue()]
        if self.use_alpha:
            color_values.append(self.color.alpha())
        self.valueChanged01.emit([x / 255.0 for x in color_values])


if __name__ == "__main__":
    from PySide2.QtWidgets import QApplication

    app = QApplication(sys.argv)

    selector = QColorSelector(use_alpha=True, use_color01=True)
    selector.show()

    sys.exit(app.exec_())
