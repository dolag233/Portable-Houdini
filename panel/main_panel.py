import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(os.path.join(current_dir, "utils"))
sys.path.append(os.path.join(current_dir, "qwidget"))
from PySide2.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QSplitter, QStatusBar, QLabel
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QPixmap, QPainter, QColor, QBrush
from menu_file import FileMenu
from menu_settings import SettingsMenu
from menu_window import WindowMenu
from menu_connection import ConnectionMenu
from hda_panel import HDAPanel
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from hou_parms_model import HouParmsModel
from hda_controller import HDAController
from remote_hda_controller import RemoteHDAController
from server_connection_dialog import ServerConnectionDialog
from utils.globals import SETTINGS_MANAGER, SettingsEnum
from panel.qwidget.qt_mesh_viewer import QMeshViewerPanel, QMeshViewer
from panel.menu_help import HelpMenu


class MainWindow(QMainWindow):
    _model = None
    _controller = None

    def __init__(self, model, controller=None):
        super().__init__()
        self._model = model
        
        # 使用远程控制器替代原有控制器
        if controller is None:
            self._controller = RemoteHDAController(model)
        else:
            self._controller = controller
            
        # 连接对话框
        self._connection_dialog = None
        
        # 连接状态指示器
        self._connection_status_label = None
        self._status_update_timer = None
        
        self.initUI()
        self.setupConnectionStatusIndicator()

    def initUI(self):
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_APP_TITLE))

        # Menu bar
        menubar = self.menuBar()

        file_menu = FileMenu(self)
        file_menu.load_hda.connect(self.updateHDA)
        file_menu.save_hip.connect(self.saveHIP)
        menubar.addMenu(file_menu)

        # 连接菜单
        connection_menu = ConnectionMenu(self._controller, self)
        connection_menu.connection_requested.connect(self.onConnectionRequested)
        connection_menu.disconnection_requested.connect(self.onDisconnectionRequested)
        connection_menu.server_settings_requested.connect(self.openServerConnectionDialog)
        menubar.addMenu(connection_menu)

        settings_menu = SettingsMenu(self)
        menubar.addMenu(settings_menu)

        window_menu = WindowMenu(self)
        menubar.addMenu(window_menu)
        window_menu.open_mesh_viewer.connect(self.onOpenMeshViewer)

        help_menu = HelpMenu(self)
        menubar.addMenu(help_menu)

        # Main widget
        self.main_widget = QWidget()
        main_widget_layout = QHBoxLayout()
        hda_mesh_splitter = QSplitter()
        self.hda_panel = HDAPanel(self._model, self._controller)
        self.mesh_viewer_panel = QMeshViewerPanel()
        self.mesh_viewer_panel.set_auto_update_model.connect(self.setAutoUpdateModel)
        self.mesh_viewer_panel.hide()
        hda_mesh_splitter.addWidget(self.hda_panel)
        hda_mesh_splitter.addWidget(self.mesh_viewer_panel)
        main_widget_layout.addWidget(hda_mesh_splitter)
        self.main_widget.setLayout(main_widget_layout)
        self.setCentralWidget(self.main_widget)

        # 启动时自动连接到远程服务器
        if SETTINGS_MANAGER.get(SettingsEnum.AUTO_CONNECT):
            host = SETTINGS_MANAGER.get(SettingsEnum.REMOTE_HOST)
            port = SETTINGS_MANAGER.get(SettingsEnum.REMOTE_PORT)
            print(f"启动时自动连接到 {host}:{port}")
            self._controller.connect_to_server(host, port)
        
        # 设置状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 打开上一次打开的hda
        if len(SETTINGS_MANAGER.get(SettingsEnum.RECENT)) > 0:
            file_menu.openRecentFile(SETTINGS_MANAGER.get(SettingsEnum.RECENT)[0])

    def updateHDA(self, hda_path, hda_name):
        if self._controller is not None and self._model is not None:
            # 客户端仅支持远程模式，不再检查本地 Houdini 环境
            
            # clear
            self._controller.clearHDA()
            self._model.clearHDA()
            self.hda_panel.clearLayout(self.hda_panel.layout)

            self._controller.setCurHDAPath(hda_path)
            self._controller.setCurHDAName(hda_name)
            
            # 检查连接状态
            if not self._controller.is_connected():
                print("未连接到远程服务器")
                return
                
            success = self._controller.loadHDA()
            if success:
                self.hda_panel.setHDAName(hda_name)
                self.hda_panel.updateUI()
                self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_APP_TITLE) + " - " + hda_name)
            else:
                print("加载HDA失败")

    def saveHIP(self, hda_path):
        self._controller.saveHIP(hda_path)

    def setAutoUpdateModel(self, auto):
        self._controller.setAutoUpdateModel(auto)

    def onOpenMeshViewer(self):
        if self.mesh_viewer_panel.isHidden():
            self._controller.setAutoUpdateModel(True)
            self._controller.update_display_model.connect(self.mesh_viewer_panel.mesh_viewer.updateModel, Qt.DirectConnection)
            self._controller.updateNodeModel()
            self.mesh_viewer_panel.mesh_viewer.autoMoveCamera()
            self.mesh_viewer_panel.show()
        elif self.mesh_viewer_panel.isVisible():
            self._controller.setAutoUpdateModel(False)
            self._controller.update_display_model.disconnect()
            self.mesh_viewer_panel.hide()
    
    def openServerConnectionDialog(self):
        """打开服务器连接对话框"""
        if self._connection_dialog is None:
            self._connection_dialog = ServerConnectionDialog(self)
            # 连接信号
            self._connection_dialog.mode_changed.connect(self.onModeChanged)
            self._connection_dialog.connection_requested.connect(self.onConnectionRequested)
        
        # 设置当前模式
        current_mode = self._controller.get_mode()
        self._connection_dialog.set_mode(current_mode)
        
        self._connection_dialog.show()
    
    def onModeChanged(self, mode):
        """模式改变处理"""
        if mode != "remote":
            print(f"警告：客户端仅支持远程模式，忽略模式设置: {mode}")
            return
            
        print("切换到远程模式")
        self._controller.set_mode("remote")
        
        # 更新窗口标题
        base_title = getLocalizationStr(LANG_STR_ENUM.UI_APP_TITLE)
        self.setWindowTitle(f"{base_title} - 远程模式")
    
    def onConnectionRequested(self, host, port):
        """连接请求处理"""
        print(f"请求连接到 {host}:{port}")
        self._controller.connect_to_server(host, port)
    
    def onDisconnectionRequested(self):
        """断开连接请求处理"""
        print("请求断开连接")
        self._controller.disconnect_from_server()
    
    def setupConnectionStatusIndicator(self):
        """设置连接状态指示器"""
        # 创建状态指示器标签
        self._connection_status_label = QLabel()
        self._connection_status_label.setFixedSize(100, 20)
        self._connection_status_label.setAlignment(Qt.AlignCenter)
        self._connection_status_label.setStyleSheet("""
            QLabel {
                border: 1px solid #666;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                font-weight: bold;
                margin: 0px;
            }
        """)
        
        # 添加到状态栏右侧
        self.status_bar.addPermanentWidget(self._connection_status_label)
        
        # 设置定时器更新状态
        self._status_update_timer = QTimer()
        self._status_update_timer.timeout.connect(self.updateConnectionStatus)
        self._status_update_timer.start(1000)  # 每秒更新一次
        
        # 连接控制器的状态变化信号
        if hasattr(self._controller, 'connection_status_changed'):
            self._controller.connection_status_changed.connect(self.onConnectionStatusChanged)
        
        # 初始更新状态
        self.updateConnectionStatus()
    
    def updateConnectionStatus(self):
        """更新连接状态显示"""
        if self._controller and self._controller.is_connected():
            # 连接状态 - 绿色
            self._connection_status_label.setText("🟢 已连接")
            self._connection_status_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #4CAF50;
                    border-radius: 10px;
                    padding: 2px 6px;
                    font-size: 11px;
                    font-weight: bold;
                    background-color: #E8F5E8;
                    color: #2E7D32;
                    margin: 0px;
                }
            """)
        else:
            # 断开状态 - 红色
            self._connection_status_label.setText("🔴 未连接")
            self._connection_status_label.setStyleSheet("""
                QLabel {
                    border: 1px solid #F44336;
                    border-radius: 10px;
                    padding: 2px 6px;
                    font-size: 11px;
                    font-weight: bold;
                    background-color: #FFEBEE;
                    color: #C62828;
                    margin: 0px;
                }
            """)
    
    def onConnectionStatusChanged(self, connected):
        """连接状态改变处理"""
        self.updateConnectionStatus()
        if connected:
            print("连接状态：已连接到远程服务器")
            self.status_bar.showMessage("已连接到远程服务器", 3000)
        else:
            print("连接状态：与远程服务器断开连接")
            self.status_bar.showMessage("与远程服务器断开连接", 3000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = HouParmsModel()
    controller = HDAController(model)
    window = MainWindow(model, controller)
    window.show()
    sys.exit(app.exec_())
