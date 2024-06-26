import sys
from PySide2.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PySide2.QtCore import Qt, QPoint
from PySide2.QtGui import QSurfaceFormat
from OpenGL.GL import *
from OpenGL.GLU import *
import math


class QMeshViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        super(QMeshViewer, self).__init__(parent)
        # 设置8倍MSAA
        fmt = QSurfaceFormat()
        fmt.setSamples(8)
        self.setFormat(fmt)

        self.vertices = []
        self.faces = []
        self.camera_angle_x = 0
        self.camera_angle_y = 0
        self.camera_distance = 10
        self.camera_x = 0
        self.camera_y = 0
        self.last_mouse_position = None
        self.loadGeometry()

    def loadGeometry(self):
        # 示例立方体顶点数据
        self.vertices = [
            (-1.0, -1.0, -1.0),
            (1.0, -1.0, -1.0),
            (1.0, 1.0, -1.0),
            (-1.0, 1.0, -1.0),
            (-1.0, -1.0, 1.0),
            (1.0, -1.0, 1.0),
            (1.0, 1.0, 1.0),
            (-1.0, 1.0, 1.0)
        ]

        # 立方体的面数据
        self.faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (0, 3, 7, 4),
            (1, 2, 6, 5)
        ]

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)  # 开启多重采样

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(
            self.camera_x,
            self.camera_y,
            self.camera_distance,
            self.camera_x,
            self.camera_y,
            0,
            0, 1, 0
        )

        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)

        # 绘制坐标平面
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)  # X轴为红色
        glVertex3f(-100.0, 0.0, 0.0)
        glVertex3f(100.0, 0.0, 0.0)
        glColor3f(0.0, 1.0, 0.0)  # Y轴为绿色
        glVertex3f(0.0, -100.0, 0.0)
        glVertex3f(0.0, 100.0, 0.0)
        glColor3f(0.0, 0.0, 1.0)  # Z轴为蓝色
        glVertex3f(0.0, 0.0, -100.0)
        glVertex3f(0.0, 0.0, 100.0)
        glEnd()

        # 绘制立方体面
        glColor3f(0.5, 0.5, 0.5)  # 灰色
        glBegin(GL_QUADS)
        for face in self.faces:
            for vertex in face:
                glVertex3f(self.vertices[vertex][0], self.vertices[vertex][1], self.vertices[vertex][2])
        glEnd()

        # 绘制立方体边线
        glColor3f(1.0, 1.0, 1.0)  # 白色
        glBegin(GL_LINES)
        for face in self.faces:
            for i in range(len(face)):
                glVertex3f(self.vertices[face[i]][0], self.vertices[face[i]][1], self.vertices[face[i]][2])
                glVertex3f(self.vertices[face[(i + 1) % len(face)]][0], self.vertices[face[(i + 1) % len(face)]][1],
                           self.vertices[face[(i + 1) % len(face)]][2])
        glEnd()

        # 绘制顶点
        glColor3f(1.0, 0.0, 0.0)  # 红色
        glPointSize(5.0)
        glBegin(GL_POINTS)
        for vertex in self.vertices:
            glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

    def loadHouNodeAsModel(self, hou_node):
        self.vertices = []
        self.faces = []

        # 读取 Houdini 节点的几何数据
        geometry = hou_node.geometry()
        points = geometry.points()
        polys = geometry.prims()

        # 提取顶点
        for point in points:
            position = point.position()
            self.vertices.append((position[0], position[1], position[2]))

        # 提取面
        for poly in polys:
            vertices = poly.vertices()
            face = []
            for vertex in vertices:
                face.append(vertex.point().number())
            self.faces.append(face)

        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton:
            self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_position is not None:
            delta = event.pos() - self.last_mouse_position
            if event.buttons() & Qt.LeftButton:
                self.camera_angle_x += delta.y() * 0.5
                self.camera_angle_y += delta.x() * 0.5
            elif event.buttons() & Qt.MiddleButton:
                self.camera_x -= delta.x() * 0.05
                self.camera_y += delta.y() * 0.05
            self.last_mouse_position = event.pos()
            self.update()

    def wheelEvent(self, event):
        angle = event.angleDelta().y() / 120
        self.camera_distance -= angle
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("3D Model Viewer")
        self.setGeometry(100, 100, 800, 600)
        self.glWidget = QMeshViewer(self)
        self.setCentralWidget(self.glWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
