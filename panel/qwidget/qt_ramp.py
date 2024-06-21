import sys
from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout, QComboBox
from PySide2.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath, QPalette
from PySide2.QtCore import Qt, QPointF, Signal

class QRamp(QWidget):
    edit_finished = Signal(dict)
    pointAdded = Signal(QPointF)
    pointRemoved = Signal(int)

    def __init__(self):
        super().__init__()
        self.points = [QPointF(0.1, 0.5), QPointF(0.3, 0.2), QPointF(0.7, 0.8), QPointF(0.9, 0.4)]
        self.selected_point = None
        self.interpolation_mode = 'Catmull-Rom'
        self.initUI()

    def initUI(self):
        self.setMinimumSize(400, 50)

    def setInterpolationMode(self, mode):
        self.interpolation_mode = mode
        self.update()
        self.edit_finished.emit(self.getHouRampParms())

    def setInterpolationModeFromBasis(self, basis):
        import hou
        interpolation = "Linear"
        if basis == hou.rampBasis.Linear:
            interpolation = "Linear"
        elif basis == hou.rampBasis.CatmullRom:
            interpolation = "Catmull-Rom"
        self.setInterpolationMode(interpolation)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        palette = self.palette()
        bg_color = color = palette.color(QPalette.Background)
        painter.setBrush(QBrush(bg_color))
        painter.drawRect(self.rect())

        # 获取插值后的点
        interp_points = self.getInterpolatedPoints()

        # 绘制曲线和填充区域
        path = QPainterPath()
        fill_path = QPainterPath()

        if interp_points:
            fill_points = interp_points.copy()
            fill_points.insert(0, QPointF(0, 0))
            fill_points.append(QPointF(1, 0))

            path.moveTo(self.mapToScene(fill_points[0]))
            fill_path.moveTo(self.width() * 0.05, self.height() * 0.95)

            for point in fill_points:
                path.lineTo(self.mapToScene(point))
                fill_path.lineTo(self.mapToScene(point))

            fill_path.lineTo(self.width() * 0.95, self.height() * 0.95)
            painter.setBrush(QBrush(QColor(200, 200, 200)))
            painter.drawPath(fill_path)

            painter.setPen(QPen(QColor(Qt.darkGray), 2))
            painter.drawPath(path)

        # 绘制控制点
        for point in self.points:
            painter.setBrush(QBrush(Qt.darkGray))
            painter.drawEllipse(self.mapToScene(point), 3, 3)

        # 绘制XY轴
        painter.setPen(QPen(QColor(Qt.darkGray), 1))
        painter.drawLine(self.width() * 0.05, self.height() * 0.95, self.width() * 0.95, self.height() * 0.95)
        painter.drawLine(self.width() * 0.05, self.height() * 0.95, self.width() * 0.05, self.height() * 0.05)

    def sampleRamp(self, posx):
        if not self.points:
            return None

        self.points.sort(key=lambda p: p.x())
        sample_points = self.points.copy()
        if self.points[0].x() > 0:
            sample_points.insert(0, QPointF(0, 0))
        if self.points[-1].x() < 1:
            sample_points.append(QPointF(1, 0))

        if posx <= sample_points[0].x():
            return sample_points[0].y()
        if posx >= sample_points[-1].x():
            return sample_points[-1].y()

        for i in range(len(sample_points) - 1):
            if sample_points[i].x() <= posx <= sample_points[i + 1].x():
                ratio = (posx - sample_points[i].x()) / (sample_points[i + 1].x() - sample_points[i].x())
                return sample_points[i].y() * (1 - ratio) + sample_points[i + 1].y() * ratio

        return ValueError(f"Unexpected posx: {posx}")

    def getInterpolatedPoints(self):
        if self.interpolation_mode == 'Linear':
            return self.points
        elif self.interpolation_mode == 'Catmull-Rom':
            return self.catmullRomInterpolation()
        return self.points

    def mapToScene(self, point):
        x = self.width() * 0.05 + point.x() * (self.width() * 0.9)
        y = self.height() * 0.95 - point.y() * (self.height() * 0.9)
        return QPointF(x, y)

    def mapFromScene(self, point):
        x = (point.x() - self.width() * 0.05) / (self.width() * 0.9)
        y = (self.height() * 0.95 - point.y()) / (self.height() * 0.9)
        return QPointF(x, y)

    def mousePressEvent(self, event):
        scene_pos = self.mapFromScene(event.pos())
        for point in self.points:
            if (point - scene_pos).manhattanLength() < 0.075:
                if event.button() == Qt.RightButton:
                    self.points.remove(point)
                    self.update()
                    return
                else:
                    self.selected_point = point
                    return
        if event.button() == Qt.LeftButton:
            self.selected_point = self.addPointFromPoint(scene_pos)

    def addPointFromPos(self, posx, posy):
        posx = 1 if posx > 1 else posx
        posx = 0 if posx < 0 else posx
        posy = 1 if posy > 1 else posy
        posy = 0 if posy < 0 else posy
        point = QPointF(posx, posy)
        self.points.append(point)
        self.points.sort(key=lambda p: p.x())
        self.update()
        return point

    def addPointFromPoint(self, pos):
        if isinstance(pos, QPointF):
            return self.addPointFromPos(pos.x(), pos.y())
        return None

    def clearPoints(self):
        self.points.clear()

    def mouseMoveEvent(self, event):
        if self.selected_point:
            scene_pos = self.mapFromScene(event.pos())
            x = scene_pos.x()
            x = 1 if x > 1 else x
            x = 0 if x < 0 else x
            scene_pos.setX(x)
            self.selected_point.setX(scene_pos.x())
            self.selected_point.setY(max(0, min(scene_pos.y(), 1)))
            self.points.sort(key=lambda p: p.x())
            self.update()

    def mouseReleaseEvent(self, event):
        self.selected_point = None
        self.edit_finished.emit(self.getHouRampParms())

    def catmullRomInterpolation(self):
        # Catmull-Rom 插值
        def catmullRom(p0, p1, p2, p3, t):
            return max(0.5 * ((2 * p1) +
                          (-p0 + p2) * t +
                          (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                          (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t), 0)

        interp_points = []
        n = len(self.points)
        for i in range(n - 1):
            p0 = self.points[max(0, i - 1)]
            p1 = self.points[i]
            p2 = self.points[min(i + 1, n - 1)]
            p3 = self.points[min(i + 2, n - 1)]

            for t in range(20):
                t /= 20
                x = catmullRom(p0.x(), p1.x(), p2.x(), p3.x(), t)
                y = catmullRom(p0.y(), p1.y(), p2.y(), p3.y(), t)
                interp_points.append(QPointF(x, y))
        interp_points.append(self.points[-1])
        return interp_points

    def getHouRampParms(self):
        import hou
        keys = [p.x() for p in self.points]
        values = [p.y() for p in self.points]
        basis = hou.rampBasis.Linear
        if self.interpolation_mode == "Linear":
            basis = hou.rampBasis.Linear
        elif self.interpolation_mode == "Catmull-Rom":
            basis = hou.rampBasis.CatmullRom

        basis = [basis for _ in range(len(keys))]
        return {"keys": keys, "values": values, "basis": basis}


class QRampWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.ramp_widget = QRamp()
        self.layout.addWidget(self.ramp_widget)

        self.interp_combo = QComboBox()
        self.interp_combo.addItems(['Linear', 'Catmull-Rom'])
        self.interp_combo.currentTextChanged.connect(self.ramp_widget.setInterpolationMode)
        self.ramp_widget.setInterpolationMode(self.interp_combo.currentText())
        self.layout.addWidget(self.interp_combo)

    def setInterpolationModeFromBasis(self, basis):
        import hou
        interpolation = "Linear"
        if basis == hou.rampBasis.Linear:
            interpolation = "Linear"
        elif basis == hou.rampBasis.CatmullRom:
            interpolation = "Catmull-Rom"
        self.interp_combo.setCurrentText(interpolation)

if __name__ == "__main__":
    app = QApplication([])
    window = QRampWidget()
    window.show()
    app.exec_()
