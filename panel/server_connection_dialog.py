#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Server Connection Dialog
服务器连接设置对话框
"""

from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, 
                               QLabel, QLineEdit, QSpinBox, QPushButton, 
                               QCheckBox, QGroupBox, QComboBox, QTextEdit,
                               QProgressBar, QFrame)
import subprocess
import os
import sys
import threading
from PySide2.QtCore import Qt, Signal, QTimer
from PySide2.QtGui import QFont
from utils.localization import LANG_STR_ENUM, getLocalizationStr
from utils.houdini_client import get_connection_manager


class ServerConnectionDialog(QDialog):
    """服务器连接设置对话框"""
    
    mode_changed = Signal(str)  # 模式改变信号
    connection_requested = Signal(str, int)  # 连接请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connection_manager = get_connection_manager()
        
        # 本地服务器管理
        self._local_server_process = None
        self._local_server_running = False
        
        self.setup_ui()
        self.load_settings()
        self.connect_signals()
        
        # 初始化时更新连接状态
        self.update_initial_connection_status()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_DIALOG_TITLE))
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # 连接设置
        self.setup_connection_group(layout)
        
        # 连接状态
        self.setup_status_group(layout)
        
        # 按钮
        self.setup_buttons(layout)
        
        self.setLayout(layout)
    

    
    def setup_connection_group(self, parent_layout):
        """设置连接设置组"""
        self.connection_group = QGroupBox(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_GROUP_TITLE))
        layout = QGridLayout()
        
        # 服务器地址
        layout.addWidget(QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_HOST)), 0, 0)
        self.host_edit = QLineEdit()
        self.host_edit.setText("localhost")
        layout.addWidget(self.host_edit, 0, 1)
        
        # 端口
        layout.addWidget(QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_PORT)), 1, 0)
        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1024, 65535)
        self.port_spinbox.setValue(18811)
        layout.addWidget(self.port_spinbox, 1, 1)
        
        # 连接超时
        layout.addWidget(QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_TIMEOUT)), 2, 0)
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 60)
        self.timeout_spinbox.setValue(10)
        layout.addWidget(self.timeout_spinbox, 2, 1)
        
        # 自动重连
        self.auto_reconnect_checkbox = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_AUTO_RECONNECT))
        self.auto_reconnect_checkbox.setChecked(True)
        layout.addWidget(self.auto_reconnect_checkbox, 3, 0, 1, 2)
        
        # 重连间隔
        layout.addWidget(QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_RETRY_INTERVAL)), 4, 0)
        self.retry_interval_spinbox = QSpinBox()
        self.retry_interval_spinbox.setRange(1, 60)
        self.retry_interval_spinbox.setValue(5)
        layout.addWidget(self.retry_interval_spinbox, 4, 1)
        
        # 最大重试次数
        layout.addWidget(QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_MAX_RETRIES)), 5, 0)
        self.max_retries_spinbox = QSpinBox()
        self.max_retries_spinbox.setRange(1, 10)
        self.max_retries_spinbox.setValue(3)
        layout.addWidget(self.max_retries_spinbox, 5, 1)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator, 6, 0, 1, 2)
        
        # 本地服务器启动选项
        self.local_server_checkbox = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_START_LOCAL_SERVER_CHECKBOX))
        self.local_server_checkbox.setToolTip(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_START_LOCAL_SERVER_CHECKBOX))
        layout.addWidget(self.local_server_checkbox, 7, 0, 1, 2)
        
        # 本地服务器启动按钮
        self.start_local_server_btn = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_START_LOCAL_SERVER))
        self.start_local_server_btn.setToolTip(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_START_LOCAL_SERVER))
        layout.addWidget(self.start_local_server_btn, 8, 0, 1, 2)
        
        # 本地服务器状态
        self.local_server_status_label = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOCAL_SERVER_NOT_STARTED))
        self.local_server_status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.local_server_status_label, 9, 0, 1, 2)
        
        # 启动时自动连接
        self.auto_connect_checkbox = QCheckBox(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_AUTO_CONNECT_CHECKBOX))
        self.auto_connect_checkbox.setToolTip(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_AUTO_CONNECT_CHECKBOX))
        layout.addWidget(self.auto_connect_checkbox, 10, 0, 1, 2)
        
        self.connection_group.setLayout(layout)
        parent_layout.addWidget(self.connection_group)
    
    def setup_status_group(self, parent_layout):
        """设置状态显示组"""
        group = QGroupBox(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_GROUP_TITLE))
        layout = QVBoxLayout()
        
        # 状态指示器
        status_layout = QHBoxLayout()
        self.status_label = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_DISCONNECTED))
        self.status_label.setStyleSheet("color: #666; font-weight: bold;")
        status_layout.addWidget(QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_LABEL)))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # 服务器信息
        self.server_info_label = QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_SERVER_INFO_NONE))
        self.server_info_label.setStyleSheet("color: #666; font-size: 12px;")
        
        # 连接日志
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: monospace; font-size: 11px;")
        
        layout.addLayout(status_layout)
        layout.addWidget(self.server_info_label)
        layout.addWidget(QLabel(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_LABEL)))
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def setup_buttons(self, parent_layout):
        """设置按钮"""
        button_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_CONNECT_BUTTON))
        self.connect_btn.setEnabled(True)  # 默认启用
        
        self.disconnect_btn = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_DISCONNECT_BUTTON))
        self.disconnect_btn.setEnabled(False)
        
        self.save_btn = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_SAVE_BUTTON))
        self.cancel_btn = QPushButton(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_CANCEL_BUTTON))
        
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        parent_layout.addLayout(button_layout)
    
    def connect_signals(self):
        """连接信号"""
        self.connect_btn.clicked.connect(self.connect_to_server)
        self.disconnect_btn.clicked.connect(self.disconnect_from_server)
        self.save_btn.clicked.connect(self.save_and_close)
        self.cancel_btn.clicked.connect(self.reject)
        
        # 本地服务器相关信号
        self.start_local_server_btn.clicked.connect(self.start_local_server)
        self.local_server_checkbox.stateChanged.connect(self.on_local_server_checkbox_changed)
        
        # 连接管理器信号
        self.connection_manager.connection_status_changed.connect(self.on_connection_status_changed)
        
        # 客户端信号
        client = self.connection_manager.get_client()
        if client:
            client.connected.connect(self.on_connected)
            client.disconnected.connect(self.on_disconnected)
            client.connection_error.connect(self.on_connection_error)
    
    def on_mode_changed(self, mode_text):
        """模式改变处理 - 已移除"""
        pass
    
    def update_mode_description(self):
        """更新模式描述 - 已移除"""
        pass
    
    def update_initial_connection_status(self):
        """初始化时更新连接状态"""
        # 检查连接管理器的当前状态
        if self.connection_manager and hasattr(self.connection_manager, 'client'):
            client = self.connection_manager.client
            if client and hasattr(client, 'is_connected') and client.is_connected:
                # 如果已连接，更新UI状态
                self.on_connection_status_changed(True)
                self.update_server_info()
            else:
                # 如果未连接，确保UI状态正确
                self.on_connection_status_changed(False)
    

    
    def connect_to_server(self):
        """连接到服务器"""
        host = self.host_edit.text().strip()
        port = self.port_spinbox.value()
        
        if not host:
            self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_ERROR_NO_HOST))
            return
        
        # 禁用连接按钮，避免重复点击
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_CONNECTING))
        
        self.add_log(f"{getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_CONNECTING)} {host}:{port}...")
        
        # 异步连接，避免界面卡死
        def connect_async():
            try:
                self.connection_requested.emit(host, port)
            except Exception as e:
                self.add_log(f"{getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_ERROR)}: {e}")
            finally:
                # 重新启用连接按钮
                self.connect_btn.setEnabled(True)
                self.connect_btn.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_CONNECT_BUTTON))
        
        import threading
        thread = threading.Thread(target=connect_async)
        thread.daemon = True
        thread.start()
    
    def disconnect_from_server(self):
        """断开服务器连接"""
        self.connection_manager.disconnect()
        self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_DISCONNECTED))
    
    def on_connection_status_changed(self, connected):
        """连接状态改变处理"""
        if connected:
            self.status_label.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_CONNECTED))
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.connect_btn.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_CONNECT_BUTTON))
            self.disconnect_btn.setEnabled(True)
            self.update_server_info()
        else:
            self.status_label.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_DISCONNECTED))
            self.status_label.setStyleSheet("color: #666; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.connect_btn.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_CONNECT_BUTTON))
            self.disconnect_btn.setEnabled(False)
            self.server_info_label.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_SERVER_INFO_NONE))
    
    def on_connected(self):
        """连接成功处理"""
        self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_SUCCESS))
    
    def on_disconnected(self):
        """断开连接处理"""
        self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_DISCONNECTED))
    
    def on_connection_error(self, error_msg):
        """连接错误处理"""
        self.add_log(f"{getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_ERROR)}: {error_msg}")
    
    def update_server_info(self):
        """更新服务器信息"""
        client = self.connection_manager.get_client()
        if client and client.is_server_connected():
            result = client.get_server_info()
            if result:
                info = f"Houdini版本: {result.get('houdini_version', 'Unknown')}"
                if result.get('current_hda'):
                    info += f" | 当前HDA: {result.get('current_hda')}"
                self.server_info_label.setText(info)
    
    def add_log(self, message):
        """添加日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def load_settings(self):
        """加载设置"""
        from utils.globals import SETTINGS_MANAGER
        from utils.settings_manager import SettingsEnum
        
        # 从全局设置管理器加载设置
        self.host_edit.setText(SETTINGS_MANAGER.get(SettingsEnum.REMOTE_HOST))
        self.port_spinbox.setValue(SETTINGS_MANAGER.get(SettingsEnum.REMOTE_PORT))
        self.timeout_spinbox.setValue(SETTINGS_MANAGER.get(SettingsEnum.CONNECTION_TIMEOUT))
        self.auto_reconnect_checkbox.setChecked(SETTINGS_MANAGER.get(SettingsEnum.AUTO_RECONNECT))
        self.auto_connect_checkbox.setChecked(SETTINGS_MANAGER.get(SettingsEnum.AUTO_CONNECT))
        
        # 设置默认值
        self.retry_interval_spinbox.setValue(5)
        self.max_retries_spinbox.setValue(3)
    
    def save_settings(self):
        """保存设置"""
        from utils.globals import SETTINGS_MANAGER
        from utils.settings_manager import SettingsEnum
        
        # 保存到全局设置管理器
        SETTINGS_MANAGER.set(SettingsEnum.REMOTE_HOST, self.host_edit.text().strip())
        SETTINGS_MANAGER.set(SettingsEnum.REMOTE_PORT, self.port_spinbox.value())
        SETTINGS_MANAGER.set(SettingsEnum.CONNECTION_TIMEOUT, self.timeout_spinbox.value())
        SETTINGS_MANAGER.set(SettingsEnum.AUTO_RECONNECT, self.auto_reconnect_checkbox.isChecked())
        SETTINGS_MANAGER.set(SettingsEnum.AUTO_CONNECT, self.auto_connect_checkbox.isChecked())
        SETTINGS_MANAGER.saveSettings()
        
        self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_SETTINGS_SAVED))
    
    def save_and_close(self):
        """保存并关闭"""
        self.save_settings()
        self.accept()
    
    def get_current_mode(self):
        """获取当前模式"""
        return "remote"  # 仅支持远程模式
    
    def set_mode(self, mode):
        """设置模式"""
        # 仅支持远程模式，忽略其他模式设置
        if mode != "remote":
            print(f"警告：客户端仅支持远程模式，忽略模式设置: {mode}")
        pass
    
    def on_local_server_checkbox_changed(self, state):
        """本地服务器选择框状态改变"""
        if state == 2:  # 选中
            self.start_local_server()
        else:  # 取消选中
            self.stop_local_server()
    
    def start_local_server(self):
        """启动本地服务器"""
        if self._local_server_running:
            self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOCAL_SERVER_RUNNING))
            return
        
        self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_STARTING_SERVER))
        
        # 在后台线程中启动服务器
        def start_server_thread():
            try:
                # 查找项目根目录中的 server_launcher.py
                current_dir = os.path.dirname(os.path.abspath(__file__))
                project_root = os.path.dirname(current_dir)
                server_launcher_path = os.path.join(project_root, "server_launcher.py")
                
                if not os.path.exists(server_launcher_path):
                    self.add_log(f"错误: 未找到 server_launcher.py 文件: {server_launcher_path}")
                    return
                
                # 启动服务器进程
                port = self.port_spinbox.value()
                cmd = [sys.executable, server_launcher_path, "--port", str(port)]
                
                self.add_log(f"执行命令: {' '.join(cmd)}")
                
                self._local_server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_root
                )
                
                self._local_server_running = True
                self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_SERVER_STARTED))
                
                # 更新UI状态
                self.update_local_server_status()
                
                # 等待一段时间后自动连接
                import time
                time.sleep(3)  # 等待服务器完全启动
                
                # 自动连接到本地服务器
                self.connect_to_server()
                
            except Exception as e:
                self.add_log(f"{getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_ERROR)}: {e}")
                self._local_server_running = False
                self.update_local_server_status()
        
        # 在后台线程中启动
        thread = threading.Thread(target=start_server_thread)
        thread.daemon = True
        thread.start()
    
    def stop_local_server(self):
        """停止本地服务器"""
        if not self._local_server_running or not self._local_server_process:
            return
        
        try:
            self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_STOPPING_SERVER))
            self._local_server_process.terminate()
            self._local_server_process.wait(timeout=5)
            self._local_server_running = False
            self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_SERVER_STOPPED))
        except Exception as e:
            self.add_log(f"{getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_ERROR)}: {e}")
            try:
                self._local_server_process.kill()
                self._local_server_running = False
                self.add_log(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_SERVER_STOPPED))
            except:
                pass
        
        self.update_local_server_status()
    
    def update_local_server_status(self):
        """更新本地服务器状态显示"""
        if self._local_server_running:
            self.local_server_status_label.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOCAL_SERVER_RUNNING))
            self.local_server_status_label.setStyleSheet("color: #4CAF50; font-size: 12px; font-weight: bold;")
            self.start_local_server_btn.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STOP_LOCAL_SERVER))
        else:
            self.local_server_status_label.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOCAL_SERVER_NOT_STARTED))
            self.local_server_status_label.setStyleSheet("color: #666; font-size: 12px;")
            self.start_local_server_btn.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_START_LOCAL_SERVER))
    
    def closeEvent(self, event):
        """关闭事件处理"""
        # 关闭对话框时停止本地服务器
        if self._local_server_running:
            self.stop_local_server()
        event.accept() 