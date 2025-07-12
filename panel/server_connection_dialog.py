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
        self.setup_ui()
        self.load_settings()
        self.connect_signals()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("服务器连接设置")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # 模式选择
        self.setup_mode_group(layout)
        
        # 连接设置
        self.setup_connection_group(layout)
        
        # 连接状态
        self.setup_status_group(layout)
        
        # 按钮
        self.setup_buttons(layout)
        
        self.setLayout(layout)
    
    def setup_mode_group(self, parent_layout):
        """设置模式选择组"""
        group = QGroupBox("工作模式")
        layout = QVBoxLayout()
        
        # 仅显示远程模式信息，不提供选择
        mode_info = QLabel("远程模式：连接到远程 Houdini 服务器")
        mode_info.setStyleSheet("font-weight: bold; color: #2c5aa0;")
        
        # 模式说明
        self.mode_description = QLabel()
        self.mode_description.setWordWrap(True)
        self.mode_description.setStyleSheet("color: #666; font-size: 12px;")
        self.mode_description.setText("远程模式：连接到远程 Houdini 服务器进行 HDA 操作。需要先在服务器端启动 Houdini 服务。")
        
        layout.addWidget(mode_info)
        layout.addWidget(self.mode_description)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def setup_connection_group(self, parent_layout):
        """设置连接设置组"""
        self.connection_group = QGroupBox("连接设置")
        layout = QGridLayout()
        
        # 服务器地址
        layout.addWidget(QLabel("服务器地址:"), 0, 0)
        self.host_edit = QLineEdit()
        self.host_edit.setText("localhost")
        layout.addWidget(self.host_edit, 0, 1)
        
        # 端口
        layout.addWidget(QLabel("端口:"), 1, 0)
        self.port_spinbox = QSpinBox()
        self.port_spinbox.setRange(1024, 65535)
        self.port_spinbox.setValue(18811)
        layout.addWidget(self.port_spinbox, 1, 1)
        
        # 连接超时
        layout.addWidget(QLabel("连接超时(秒):"), 2, 0)
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(1, 60)
        self.timeout_spinbox.setValue(10)
        layout.addWidget(self.timeout_spinbox, 2, 1)
        
        # 自动重连
        self.auto_reconnect_checkbox = QCheckBox("自动重连")
        self.auto_reconnect_checkbox.setChecked(True)
        layout.addWidget(self.auto_reconnect_checkbox, 3, 0, 1, 2)
        
        # 重连间隔
        layout.addWidget(QLabel("重连间隔(秒):"), 4, 0)
        self.retry_interval_spinbox = QSpinBox()
        self.retry_interval_spinbox.setRange(1, 60)
        self.retry_interval_spinbox.setValue(5)
        layout.addWidget(self.retry_interval_spinbox, 4, 1)
        
        # 最大重试次数
        layout.addWidget(QLabel("最大重试次数:"), 5, 0)
        self.max_retries_spinbox = QSpinBox()
        self.max_retries_spinbox.setRange(1, 10)
        self.max_retries_spinbox.setValue(3)
        layout.addWidget(self.max_retries_spinbox, 5, 1)
        
        self.connection_group.setLayout(layout)
        parent_layout.addWidget(self.connection_group)
    
    def setup_status_group(self, parent_layout):
        """设置状态显示组"""
        group = QGroupBox("连接状态")
        layout = QVBoxLayout()
        
        # 状态指示器
        status_layout = QHBoxLayout()
        self.status_label = QLabel("未连接")
        self.status_label.setStyleSheet("color: #666; font-weight: bold;")
        status_layout.addWidget(QLabel("状态:"))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # 服务器信息
        self.server_info_label = QLabel("无服务器信息")
        self.server_info_label.setStyleSheet("color: #666; font-size: 12px;")
        
        # 连接日志
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: monospace; font-size: 11px;")
        
        layout.addLayout(status_layout)
        layout.addWidget(self.server_info_label)
        layout.addWidget(QLabel("连接日志:"))
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
    
    def setup_buttons(self, parent_layout):
        """设置按钮"""
        button_layout = QHBoxLayout()
        
        self.test_connection_btn = QPushButton("测试连接")
        self.test_connection_btn.setEnabled(True)  # 默认启用
        
        self.connect_btn = QPushButton("连接")
        self.connect_btn.setEnabled(True)  # 默认启用
        
        self.disconnect_btn = QPushButton("断开连接")
        self.disconnect_btn.setEnabled(False)
        
        self.save_btn = QPushButton("保存设置")
        self.cancel_btn = QPushButton("取消")
        
        button_layout.addWidget(self.test_connection_btn)
        button_layout.addWidget(self.connect_btn)
        button_layout.addWidget(self.disconnect_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        parent_layout.addLayout(button_layout)
    
    def connect_signals(self):
        """连接信号"""
        # 移除模式选择相关信号
        self.test_connection_btn.clicked.connect(self.test_connection)
        self.connect_btn.clicked.connect(self.connect_to_server)
        self.disconnect_btn.clicked.connect(self.disconnect_from_server)
        self.save_btn.clicked.connect(self.save_and_close)
        self.cancel_btn.clicked.connect(self.reject)
        
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
    
    def test_connection(self):
        """测试连接"""
        host = self.host_edit.text().strip()
        port = self.port_spinbox.value()
        
        if not host:
            self.add_log("错误: 请输入服务器地址")
            return
        
        self.add_log(f"测试连接到 {host}:{port}...")
        
        # 这里可以实现简单的连接测试
        # 暂时只是模拟
        self.add_log("连接测试完成")
    
    def connect_to_server(self):
        """连接到服务器"""
        host = self.host_edit.text().strip()
        port = self.port_spinbox.value()
        
        if not host:
            self.add_log("错误: 请输入服务器地址")
            return
        
        self.add_log(f"正在连接到 {host}:{port}...")
        self.connection_requested.emit(host, port)
    
    def disconnect_from_server(self):
        """断开服务器连接"""
        self.connection_manager.disconnect()
        self.add_log("断开连接")
    
    def on_connection_status_changed(self, connected):
        """连接状态改变处理"""
        if connected:
            self.status_label.setText("已连接")
            self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.update_server_info()
        else:
            self.status_label.setText("未连接")
            self.status_label.setStyleSheet("color: #666; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.server_info_label.setText("无服务器信息")
    
    def on_connected(self):
        """连接成功处理"""
        self.add_log("连接成功")
    
    def on_disconnected(self):
        """断开连接处理"""
        self.add_log("连接断开")
    
    def on_connection_error(self, error_msg):
        """连接错误处理"""
        self.add_log(f"连接错误: {error_msg}")
    
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
        client = self.connection_manager.get_client()
        if client:
            settings = client.settings.settings
            self.host_edit.setText(settings.get("server_host", "localhost"))
            self.port_spinbox.setValue(settings.get("server_port", 18811))
            self.timeout_spinbox.setValue(settings.get("connection_timeout", 10))
            self.auto_reconnect_checkbox.setChecked(settings.get("auto_reconnect", True))
            self.retry_interval_spinbox.setValue(settings.get("retry_interval", 5))
            self.max_retries_spinbox.setValue(settings.get("max_retries", 3))
    
    def save_settings(self):
        """保存设置"""
        client = self.connection_manager.get_client()
        if client:
            settings = client.settings.settings
            settings["server_host"] = self.host_edit.text().strip()
            settings["server_port"] = self.port_spinbox.value()
            settings["connection_timeout"] = self.timeout_spinbox.value()
            settings["auto_reconnect"] = self.auto_reconnect_checkbox.isChecked()
            settings["retry_interval"] = self.retry_interval_spinbox.value()
            settings["max_retries"] = self.max_retries_spinbox.value()
            client.settings.save_settings()
    
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