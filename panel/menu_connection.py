#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Connection Menu
连接菜单 - 类似虚幻引擎的 Connect Session 菜单
"""

from PySide2.QtWidgets import QMenu, QAction, QActionGroup, QMessageBox
from PySide2.QtCore import Signal, QTimer
from PySide2.QtGui import QIcon
from utils.globals import SETTINGS_MANAGER
from utils.settings_manager import SettingsEnum
from utils.localization import LANG_STR_ENUM, getLocalizationStr


class ConnectionMenu(QMenu):
    """连接菜单"""
    
    # 信号定义
    connection_requested = Signal(str, int)  # 连接请求信号
    disconnection_requested = Signal()      # 断开连接请求信号
    server_settings_requested = Signal()    # 服务器设置请求信号
    
    def __init__(self, controller, parent=None):
        super().__init__(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_MENU), parent)
        self.controller = controller
        self.setup_menu()
        self.setup_timer()
        
        # 连接控制器信号
        if hasattr(self.controller, 'connection_status_changed'):
            self.controller.connection_status_changed.connect(self.on_connection_status_changed)
    
    def setup_menu(self):
        """设置菜单"""
        # 连接状态指示器
        self.connection_status_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_DISCONNECTED), self)
        self.connection_status_action.setEnabled(False)
        self.addAction(self.connection_status_action)
        
        self.addSeparator()
        
        # 快速连接动作
        self.quick_connect_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_QUICK_CONNECT), self)
        self.quick_connect_action.setToolTip(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_QUICK_CONNECT))
        self.quick_connect_action.triggered.connect(self.quick_connect)
        self.addAction(self.quick_connect_action)
        
        # 断开连接动作
        self.disconnect_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_DISCONNECT), self)
        self.disconnect_action.setEnabled(False)
        self.disconnect_action.triggered.connect(self.disconnect)
        self.addAction(self.disconnect_action)
        
        # 本地服务器操作
        self.start_local_server_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_START_LOCAL_SERVER), self)
        self.start_local_server_action.triggered.connect(self.start_local_server)
        self.addAction(self.start_local_server_action)
        
        self.stop_local_server_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STOP_LOCAL_SERVER), self)
        self.stop_local_server_action.setEnabled(False)
        self.stop_local_server_action.triggered.connect(self.stop_local_server)
        self.addAction(self.stop_local_server_action)
        
        self.addSeparator()
        
        # 连接设置
        self.connection_settings_action = QAction(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_SETTINGS), self)
        self.connection_settings_action.triggered.connect(self.open_connection_settings)
        self.addAction(self.connection_settings_action)
    

    
    def setup_timer(self):
        """设置定时器"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_connection_status)
        self.status_timer.start(2000)  # 每2秒更新一次状态
    
    def quick_connect(self):
        """快速连接"""
        host = SETTINGS_MANAGER.get(SettingsEnum.REMOTE_HOST)
        port = SETTINGS_MANAGER.get(SettingsEnum.REMOTE_PORT)
        
        if not host:
            QMessageBox.warning(self, getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_LOG_ERROR), 
                              getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_ERROR_CONFIG_HOST))
            return
        
        print(f"快速连接到 {host}:{port}")
        self.connection_requested.emit(host, port)
    
    def disconnect(self):
        """断开连接"""
        print("断开连接")
        self.disconnection_requested.emit()
    

    
    def start_local_server(self):
        """启动本地服务器"""
        # 这里可以集成本地服务器启动逻辑
        print("启动本地服务器")
        # 暂时显示消息
        QMessageBox.information(self, "本地服务器", "本地服务器启动功能请在连接设置中使用")
    
    def stop_local_server(self):
        """停止本地服务器"""
        print("停止本地服务器")
    
    def open_connection_settings(self):
        """打开连接设置"""
        self.server_settings_requested.emit()
    

    
    def update_connection_status(self):
        """更新连接状态"""
        if self.controller and self.controller.is_connected():
            # 已连接状态
            self.connection_status_action.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_CONNECTED))
            self.quick_connect_action.setEnabled(False)
            self.disconnect_action.setEnabled(True)
            
            # 获取服务器信息
            try:
                # 这里可以获取服务器信息并显示
                host = SETTINGS_MANAGER.get(SettingsEnum.REMOTE_HOST)
                port = SETTINGS_MANAGER.get(SettingsEnum.REMOTE_PORT)
                connected_text = getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_CONNECTED)
                self.connection_status_action.setText(f"{connected_text} {host}:{port}")
            except:
                self.connection_status_action.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_CONNECTED))
        else:
            # 未连接状态
            self.connection_status_action.setText(getLocalizationStr(LANG_STR_ENUM.UI_CONNECTION_STATUS_DISCONNECTED))
            self.quick_connect_action.setEnabled(True)
            self.disconnect_action.setEnabled(False)
    
    def on_connection_status_changed(self, connected):
        """连接状态改变处理"""
        self.update_connection_status()
        
        if connected:
            pass  # 连接成功后的处理 