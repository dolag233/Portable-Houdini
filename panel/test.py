from PySide2.QtWidgets import QApplication
from PySide2.QtCore import Qt
from panel.qwidget.qt_float_slider import QFloatSlider
from panel.utils.simple_enum import SimpleEnum

class E(SimpleEnum):
    A = None
    B = None

class D(SimpleEnum):
    A = None
    B = None
print(E.A)
print(D.A)



# 创建一个QApplication实例
app = QApplication([])

# 创建一个QDoubleSpinBox实例
spinbox = QFloatSlider(Qt.Horizontal)

# 设置范围和初始值
spinbox.setRange(0.0, 100.0)
spinbox.setValue(25.0)
spinbox.floatSliderReleased.connect(lambda x: print(x))

# 显示QDoubleSpinBox
spinbox.show()

# 进入主循环
app.exec_()