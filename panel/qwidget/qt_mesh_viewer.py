import sys
from PySide2.QtWidgets import (QApplication, QMainWindow, QOpenGLWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
                               QPushButton, QWidget, QDockWidget, QGridLayout, QGroupBox, QSplitter)
from PySide2.QtCore import Qt, QPoint, QTimer, Signal
from PySide2.QtGui import QSurfaceFormat
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from panel.utils.localization import getLocalizationStr, LANG_STR_ENUM


class QMeshViewer(QOpenGLWidget):
    update_counter_label = Signal(list)

    def __init__(self, parent=None):
        super(QMeshViewer, self).__init__(parent)
        # 设置8倍MSAA
        fmt = QSurfaceFormat()
        fmt.setSamples(8)
        self.setFormat(fmt)

        self.vertices = []
        self.vertex_colors = []
        self.faces = []
        self.vertex_count = 0
        self.face_count = 0
        self.show_vertex_colors = False
        self.auto_update_model = False

        self.camera_angle_x = 0
        self.camera_angle_y = 0
        self.camera_distance = 10
        self.camera_x = 0
        self.camera_y = 0

        self.show_grid = True
        self.grid_spacing = 1

        self.last_mouse_position = None
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        self.vertex_count = len(self.vertices)
        self.face_count = len(self.faces)

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

        glClearColor(0.08, 0.08, 0.11, 1.0)

        glRotatef(self.camera_angle_x, 1, 0, 0)
        glRotatef(self.camera_angle_y, 0, 1, 0)

        # Draw the grid and axes
        self.drawGridAndAxes()

        # 绘制立方体面
        if self.show_vertex_colors:
            glBegin(GL_QUADS)
            for face in self.faces:
                for vertex in face:
                    glColor3f(*self.vertex_colors[vertex])
                    glVertex3f(self.vertices[vertex][0], self.vertices[vertex][1], self.vertices[vertex][2])
            glEnd()
        else:
            glColor3f(0.5, 0.5, 0.5)  # 灰色
            glBegin(GL_QUADS)
            for face in self.faces:
                for vertex in face:
                    glVertex3f(self.vertices[vertex][0], self.vertices[vertex][1], self.vertices[vertex][2])
            glEnd()

        # 绘制立方体边线
        glColor3f(0.5, 0.5, 0.5)  # 白色
        glBegin(GL_LINES)
        for face in self.faces:
            for i in range(len(face)):
                glVertex3f(self.vertices[face[i]][0], self.vertices[face[i]][1], self.vertices[face[i]][2])
                glVertex3f(self.vertices[face[(i + 1) % len(face)]][0], self.vertices[face[(i + 1) % len(face)]][1], self.vertices[face[(i + 1) % len(face)]][2])
        glEnd()

        # 绘制顶点
        glColor3f(0.02, 0.1, 0.6)  # 暗蓝色
        glPointSize(5.0)
        glBegin(GL_POINTS)
        for vertex in self.vertices:
            glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

    def drawGridAndAxes(self):
        if self.show_grid:
            # Adjust grid spacing based on camera distance
            grid_spacing = 1
            while self.camera_distance > grid_spacing * 10:
                grid_spacing *= 10
            self.grid_spacing = grid_spacing

            # Draw the main grid on the XZ plane with thick lines
            glColor3f(0.5, 0.5, 0.5)
            glLineWidth(2.0)  # Thick lines for the main grid
            glBegin(GL_LINES)
            for i in range(-100, 101, self.grid_spacing):
                glVertex3f(i, 0, -100)
                glVertex3f(i, 0, 100)
                glVertex3f(-100, 0, i)
                glVertex3f(100, 0, i)
            glEnd()

            # Draw the subdivided grid on the XZ plane with thin lines
            fine_spacing = self.grid_spacing / 10.0
            glLineWidth(0.75)  # Thin lines for the subdivided grid
            glBegin(GL_LINES)
            for i in range(int(-100 / fine_spacing), int(101 / fine_spacing)):
                if i % 10 != 0:  # Skip main grid lines
                    glVertex3f(i * fine_spacing, 0, -100)
                    glVertex3f(i * fine_spacing, 0, 100)
                    glVertex3f(-100, 0, i * fine_spacing)
                    glVertex3f(100, 0, i * fine_spacing)
            glEnd()

        # Draw the axes
        glLineWidth(3.0)  # Restore line width for the axes
        glBegin(GL_LINES)
        glColor3f(1.0, 0.0, 0.0)  # X axis red
        glVertex3f(-100.0, 0.0, 0.0)
        glVertex3f(100.0, 0.0, 0.0)
        glColor3f(0.0, 1.0, 0.0)  # Y axis green
        glVertex3f(0.0, 0, 0.0)
        glVertex3f(0.0, 100.0, 0.0)
        glColor3f(0.0, 0.0, 1.0)  # Z axis blue
        glVertex3f(0.0, 0.0, -100.0)
        glVertex3f(0.0, 0.0, 100.0)
        glEnd()

    def setDisplayAxisGrid(self, display_or_not):
        self.show_grid = display_or_not
        self.update()

    def updateModel(self, vertices, vertex_colors, faces):
        self.vertices = vertices
        self.vertex_colors = vertex_colors
        self.faces = faces
        self.vertex_count = len(self.vertices)
        self.face_count = len(self.faces)
        self.update_counter_label.emit([self.vertex_count, self.face_count])
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton or event.button() == Qt.MiddleButton or event.button() == Qt.RightButton:
            self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_mouse_position is not None:
            delta = event.pos() - self.last_mouse_position
            scale_factor = self.camera_distance / 100.0  # 根据距离调整移动速度
            if event.buttons() & Qt.LeftButton:
                self.camera_angle_x += delta.y() * 0.5
                self.camera_angle_y += delta.x() * 0.5
            elif event.buttons() & Qt.MiddleButton:
                self.camera_x -= delta.x() * 0.05 * scale_factor
                self.camera_y += delta.y() * 0.05 * scale_factor
            elif event.buttons() & Qt.RightButton:
                self.camera_distance -= delta.x() * 0.05 * scale_factor
            self.last_mouse_position = event.pos()
            self.update()

    def wheelEvent(self, event):
        angle = event.angleDelta().y() / 120
        self.camera_distance -= angle
        self.update()

    def autoMoveCamera(self):
        if not self.vertices:
            return

        min_x, min_y, min_z = self.vertices[0]
        max_x, max_y, max_z = self.vertices[0]
        for vertex in self.vertices:
            min_x = min(min_x, vertex[0])
            min_y = min(min_y, vertex[1])
            min_z = min(min_z, vertex[2])
            max_x = max(max_x, vertex[0])
            max_y = max(max_y, vertex[1])
            max_z = max(max_z, vertex[2])

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0
        center_z = (min_z + max_z) / 2.0

        bbox_width = max_x - min_x
        bbox_height = max_y - min_y
        bbox_depth = max_z - min_z

        self.camera_x = center_x
        self.camera_y = center_y

        # 根据窗口尺寸调整摄像机距离
        aspect_ratio = self.width() / self.height()
        model_aspect_ratio = bbox_width / bbox_height
        if model_aspect_ratio > aspect_ratio:
            # 模型的宽高比大于窗口的宽高比
            self.camera_distance = (bbox_width / (2 * math.tan(math.radians(22.5))))
        else:
            # 模型的宽高比小于或等于窗口的宽高比
            self.camera_distance = (bbox_height / (2 * math.tan(math.radians(22.5))))

        self.camera_distance = max(self.camera_distance, bbox_depth) * 1.5
        self.camera_angle_x = 30
        self.camera_angle_y = -45

        self.update()

    def setDisplayPointColor(self, display_or_not):
        self.show_vertex_colors = display_or_not
        self.update()



class QMeshViewerPanel(QWidget):
    mesh_viewer = None

    def __init__(self):
        super(QMeshViewerPanel, self).__init__()

        self.mesh_viewer = QMeshViewer(self)

        # 顶点和面数标签
        self.vertex_label = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_INFO_VERTEX) + ": -")
        self.face_label = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_INFO_POLYGON) + ": -")
        self.mesh_viewer.update_counter_label.connect(self.updateCounterLabels)

        # 控制面板与复选框
        self.checkbox_auto_update = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_AUTO_UPDATE_NODE))
        self.checkbox_show_vertex_colors = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_VERTEX_COLOR))
        self.checkbox_show_vertex_colors.setChecked(True)
        self.mesh_viewer.setDisplayPointColor(True)
        self.checkbox_show_axis_grid = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_DISPLAY_AXIS_GRID))
        self.checkbox_show_axis_grid.setChecked(True)
        self.mesh_viewer.setDisplayAxisGrid(True)
        self.button_auto_move_camera = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_OPTIONS_PANEL_ADJUST_CAMERA))

        # 布局
        parameter_panel = QVBoxLayout()
        parameter_panel.addWidget(self.checkbox_auto_update)
        parameter_panel.addWidget(self.checkbox_show_vertex_colors)
        parameter_panel.addWidget(self.checkbox_show_axis_grid)
        parameter_panel.addWidget(self.button_auto_move_camera)
        parameter_panel.addStretch()

        control_widget = QWidget()
        control_widget.setLayout(parameter_panel)
        control_widget.setFixedWidth(200)  # Set a fixed width for control widget

        splitter = QSplitter()
        splitter.addWidget(self.mesh_viewer)
        splitter.addWidget(control_widget)
        splitter.setSizes([800, 200])  # Initial sizes, can be adjusted

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(splitter)

        # 连接信号
        self.checkbox_show_vertex_colors.toggled.connect(self.mesh_viewer.setDisplayPointColor)
        self.checkbox_show_axis_grid.toggled.connect(self.mesh_viewer.setDisplayAxisGrid)
        self.button_auto_move_camera.clicked.connect(self.mesh_viewer.autoMoveCamera)

    def updateCounterLabels(self, counts):
        vertex_count, face_count = counts[0], counts[1]
        self.vertex_label.setText("{}: {}".format(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_INFO_VERTEX), vertex_count))
        self.face_label.setText("{}: {}".format(getLocalizationStr(LANG_STR_ENUM.UI_MESH_VIEWER_INFO_POLYGON), face_count))

    def setShowVertexColors(self, value):
        self.mesh_viewer.setDisplayPointColor(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMeshViewerPanel()
    window.show()
    sys.exit(app.exec_())