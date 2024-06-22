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
        if basis == hou.rampBasis.Constant:
            interpolation = "Constant"
        elif basis == hou.rampBasis.Linear:
            interpolation = "Linear"
        elif basis == hou.rampBasis.CatmullRom:
            interpolation = "Catmull-Rom"
        elif basis == hou.rampBasis.MonotoneCubic:
            interpolation = "MonotoneCubic"
        elif basis == hou.rampBasis.Bezier:
            interpolation = "Bezier"
        elif basis == hou.rampBasis.BSpline:
            interpolation = "BSpline"
        elif basis == hou.rampBasis.Hermite:  # not support
            # interpolation = "Hermite"
            interpolation = "Catmull-Rom"
        self.setInterpolationMode(interpolation)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        palette = self.palette()
        bg_color = palette.color(QPalette.Background)
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
            fill_path.moveTo(self.mapToScene(fill_points[0]))

            for point in fill_points:
                path.lineTo(self.mapToScene(point))
                fill_path.lineTo(self.mapToScene(point))

            fill_path.lineTo(self.mapToScene(QPointF(1, 0)))
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
        painter.drawLine(self.mapToScene(QPointF(0, 0)), self.mapToScene(QPointF(1, 0)))
        painter.drawLine(self.mapToScene(QPointF(0, 0)), self.mapToScene(QPointF(0, 1)))

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

    def mapToScene(self, point):
        x = point.x() * self.width()
        y = (1 - point.y()) * self.height()
        return QPointF(x, y)

    def mapFromScene(self, point):
        x = point.x() / self.width()
        y = 1 - point.y() / self.height()
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

    def bezierInterpolation(self):
        def bezier(p0, p1, p2, p3, t):
            return (1 - t)**3 * p0 + 3 * (1 - t)**2 * t * p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3

        interp_points = []
        n = len(self.points)
        for i in range(0, n, 3):
            p0 = self.points[i]
            p1 = self.points[min(i + 1, n - 1)]
            p2 = self.points[min(i + 2, n - 1)]
            p3 = self.points[min(i + 3, n - 1)]

            for t in range(20):
                t /= 20
                x = bezier(p0.x(), p1.x(), p2.x(), p3.x(), t)
                y = bezier(p0.y(), p1.y(), p2.y(), p3.y(), t)
                interp_points.append(QPointF(x, y))
        return interp_points

    def bSplineInterpolation(self):
        points = self.points
        def bSpline(t, p0, p1, p2, p3):
            return (1 / 6) * ((1 - t) ** 3 * p0 + (4 - 6 * t ** 2 + 3 * t ** 3) * p1 + (
                        1 + 3 * t + 3 * t ** 2 - 3 * t ** 3) * p2 + t ** 3 * p3)

        interp_points = []
        n = len(points)
        for i in range(n - 1):
            p0 = points[max(0, i - 1)]
            p1 = points[i]
            p2 = points[min(i + 1, n - 1)]
            p3 = points[min(i + 2, n - 1)]

            for t in range(20):
                t /= 20
                x = bSpline(t, p0.x(), p1.x(), p2.x(), p3.x())
                y = bSpline(t, p0.y(), p1.y(), p2.y(), p3.y())
                interp_points.append(QPointF(x, y))
        interp_points.append(points[-1])
        return interp_points

    def monotoneCubicInterpolation(self):
        points = self.points
        def cubicHermite(p0, m0, p1, m1, t):
            t2 = t * t
            t3 = t2 * t
            return (2 * t3 - 3 * t2 + 1) * p0 + (t3 - 2 * t2 + t) * m0 + (-2 * t3 + 3 * t2) * p1 + (t3 - t2) * m1

        def computeTangents(points):
            n = len(points)
            tangents = [0] * n
            for i in range(1, n - 1):
                tangents[i] = (points[i + 1].y() - points[i - 1].y()) / (points[i + 1].x() - points[i - 1].x())
            tangents[0] = tangents[1]
            tangents[-1] = tangents[-2]
            return tangents

        interp_points = []
        n = len(points)
        tangents = computeTangents(points)
        for i in range(n - 1):
            p0 = points[i]
            p1 = points[i + 1]
            m0 = tangents[i] * (p1.x() - p0.x())
            m1 = tangents[i + 1] * (p1.x() - p0.x())

            for t in range(20):
                t /= 20
                x = p0.x() + t * (p1.x() - p0.x())
                y = cubicHermite(p0.y(), m0, p1.y(), m1, t)
                interp_points.append(QPointF(x, y))
        interp_points.append(points[-1])
        return interp_points

    def constantInterpolation(self):
        points = self.points
        interp_points = []
        for i in range(len(points) - 1):
            interp_points.append(points[i])
            interp_points.append(QPointF(points[i + 1].x(), points[i].y()))
        interp_points.append(points[-1])
        return interp_points

    def getInterpolatedPoints(self):
        if self.interpolation_mode == 'Linear':
            return self.points
        elif self.interpolation_mode == 'Catmull-Rom':
            return self.catmullRomInterpolation()
        elif self.interpolation_mode == 'Bezier':
            return self.bezierInterpolation()
        elif self.interpolation_mode == 'BSpline':
            return self.bSplineInterpolation()
        elif self.interpolation_mode == 'MonotoneCubic':
            return self.monotoneCubicInterpolation()
        elif self.interpolation_mode == 'Constant':
            return self.constantInterpolation()
        # elif self.interpolation_mode == 'Hermite':
        #     return self.hermiteInterpolation()
        return self.points

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
        self.interp_combo.addItems(['Constant', 'Linear', 'Catmull-Rom', 'MonotoneCubic', 'Bezier', 'BSpline'])
        self.interp_combo.setCurrentText('Catmull-Rom')
        self.interp_combo.currentTextChanged.connect(self.ramp_widget.setInterpolationMode)
        self.ramp_widget.setInterpolationMode(self.interp_combo.currentText())
        self.layout.addWidget(self.interp_combo)

    def setInterpolationModeFromBasis(self, basis):
        import hou
        interpolation = "Linear"
        if basis == hou.rampBasis.Constant:
            interpolation = "Constant"
        elif basis == hou.rampBasis.Linear:
            interpolation = "Linear"
        elif basis == hou.rampBasis.CatmullRom:
            interpolation = "Catmull-Rom"
        elif basis == hou.rampBasis.MonotoneCubic:
            interpolation = "MonotoneCubic"
        elif basis == hou.rampBasis.Bezier:
            interpolation = "Bezier"
        elif basis == hou.rampBasis.BSpline:
            interpolation = "BSpline"
        elif basis == hou.rampBasis.Hermite:  # not support
            # interpolation = "Hermite"
            interpolation = "Catmull-Rom"
        self.interp_combo.setCurrentText(interpolation)

if __name__ == "__main__":
    app = QApplication([])
    window = QRampWidget()
    window.show()
    app.exec_()
