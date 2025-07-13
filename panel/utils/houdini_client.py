#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Houdini Client
连接到远程Houdini服务器的客户端
"""

import time
import threading
import json
import os
from PySide2.QtCore import QObject, Signal, QTimer


class HoudiniClientSettings:
    """客户端设置管理"""
    
    def __init__(self, settings_file="client_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """加载客户端设置"""
        default_settings = {
            "server_host": "localhost",
            "server_port": 18811,
            "connection_timeout": 10,
            "retry_interval": 5,
            "max_retries": 3,
            "auto_reconnect": True
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 合并默认设置
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception as e:
                print(f"加载客户端设置失败: {e}")
        
        return default_settings
    
    def save_settings(self):
        """保存客户端设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存客户端设置失败: {e}")


class HoudiniClient(QObject):
    """Houdini远程客户端"""
    
    # 信号定义
    connected = Signal()
    disconnected = Signal()
    connection_error = Signal(str)
    server_response = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings = HoudiniClientSettings()
        self.connection = None
        self.hou_module = None
        self.houdini_service = None
        self.is_connected = False
        self.retry_count = 0
        self.connection_thread = None
        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self._try_reconnect)
        
    def connect_to_server(self, host=None, port=None):
        """连接到Houdini服务器"""
        if host:
            self.settings.settings["server_host"] = host
        if port:
            self.settings.settings["server_port"] = port
        
        self.settings.save_settings()
        
        # 直接在主线程中连接，避免线程问题
        self._connect_directly()
    
    def _connect_directly(self):
        """直接连接（主线程）"""
        try:
            import hrpyc
            
            host = self.settings.settings["server_host"]
            port = self.settings.settings["server_port"]
            
            print(f"正在连接到Houdini服务器 {host}:{port}...")
            
            # 连接到服务器，使用指定的主机和端口
            self.connection, self.hou_module = hrpyc.import_remote_module(server=host, port=port)
            
            # 获取远程服务对象
            self.houdini_service = self.hou_module.houdini_service
            
            self.is_connected = True
            self.retry_count = 0
            
            print("连接成功！")
            self.connected.emit()
            
        except Exception as e:
            error_msg = f"连接失败: {str(e)}"
            print(error_msg)
            self.is_connected = False
            self.connection_error.emit(error_msg)
            
            # 如果启用自动重连
            if self.settings.settings.get("auto_reconnect", True):
                self._schedule_reconnect()
    
    def _connect_thread(self):
        """连接线程"""
        try:
            import hrpyc
            
            host = self.settings.settings["server_host"]
            port = self.settings.settings["server_port"]
            
            print(f"正在连接到Houdini服务器 {host}:{port}...")
            
            # 连接到服务器，使用指定的主机和端口
            self.connection, self.hou_module = hrpyc.import_remote_module(server=host, port=port)
            
            # 获取远程服务对象
            self.houdini_service = self.hou_module.houdini_service
            
            self.is_connected = True
            self.retry_count = 0
            
            print("连接成功！")
            # 使用 QMetaObject.invokeMethod 在主线程中发送信号
            from PySide2.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self, "connected", Qt.QueuedConnection)
            
        except Exception as e:
            error_msg = f"连接失败: {str(e)}"
            print(error_msg)
            self.is_connected = False
            # 使用 QMetaObject.invokeMethod 在主线程中发送信号
            from PySide2.QtCore import QMetaObject, Qt
            QMetaObject.invokeMethod(self, "connection_error", Qt.QueuedConnection, error_msg)
            
            # 如果启用自动重连
            if self.settings.settings.get("auto_reconnect", True):
                self._schedule_reconnect()
    
    def _schedule_reconnect(self):
        """安排重连"""
        if self.retry_count < self.settings.settings.get("max_retries", 3):
            self.retry_count += 1
            retry_interval = self.settings.settings.get("retry_interval", 5) * 1000  # 转换为毫秒
            print(f"将在 {retry_interval/1000} 秒后重试连接 (第 {self.retry_count} 次)")
            # 使用 QTimer.singleShot 避免线程问题
            from PySide2.QtCore import QTimer
            QTimer.singleShot(retry_interval, self._try_reconnect)
    
    def _try_reconnect(self):
        """尝试重连"""
        self._connect_directly()
    
    def disconnect(self):
        """断开连接"""
        try:
            if self.connection:
                self.connection.close()
            self.is_connected = False
            self.connection = None
            self.hou_module = None
            self.houdini_service = None
            self.reconnect_timer.stop()
            print("已断开连接")
            self.disconnected.emit()
        except Exception as e:
            print(f"断开连接时发生错误: {e}")
    
    def is_server_connected(self):
        """检查是否连接到服务器"""
        return self.is_connected and self.connection is not None
    
    def call_remote_method(self, method_name, *args, **kwargs):
        """调用远程方法"""
        if not self.is_server_connected():
            return {"success": False, "message": "未连接到服务器"}
        
        try:
            if not hasattr(self.houdini_service, method_name):
                return {"success": False, "message": f"远程方法不存在: {method_name}"}
            
            method = getattr(self.houdini_service, method_name)
            result = method(*args, **kwargs)
            
            # 发送响应信号
            self.server_response.emit({
                "method": method_name,
                "args": args,
                "kwargs": kwargs,
                "result": result
            })
            
            return result
            
        except Exception as e:
            error_msg = f"调用远程方法失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    # 便捷方法
    def upload_file(self, file_path):
        """上传文件到服务器"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "message": f"文件不存在: {file_path}"}
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            file_size = len(file_content)
            filename = os.path.basename(file_path)
            
            print(f"正在上传文件: {filename} ({file_size} bytes)")
            
            # 直接传输二进制数据，不使用Base64编码
            result = self.call_remote_method("upload_file", file_content, filename)
            
            if result.get("success", False):
                # 验证上传的文件大小
                uploaded_size = result.get("file_size", 0)
                if uploaded_size == file_size:
                    print(f"文件上传成功: {filename} (大小验证通过)")
                else:
                    print(f"文件上传成功但大小不匹配: 原始 {file_size} vs 上传 {uploaded_size}")
            else:
                print(f"文件上传失败: {result.get('message', '未知错误')}")
            
            return result
            
        except Exception as e:
            error_msg = f"上传文件失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def load_hda(self, hda_path, hda_name=None):
        """加载HDA"""
        return self.call_remote_method("load_hda", hda_path, hda_name)
    
    def set_parameter(self, parm_name, value):
        """设置参数"""
        return self.call_remote_method("set_parameter", parm_name, value)
    
    def set_parameters(self, parameters):
        """批量设置参数"""
        return self.call_remote_method("set_parameters", parameters)
    
    def get_parameter(self, parm_name):
        """获取参数"""
        return self.call_remote_method("get_parameter", parm_name)
    
    def get_all_parameters(self):
        """获取所有参数"""
        return self.call_remote_method("get_all_parameters")
    
    def save_hip(self, file_path):
        """保存HIP文件"""
        return self.call_remote_method("save_hip", file_path)
    
    def set_auto_update_model(self, auto_update):
        """设置自动更新模型"""
        return self.call_remote_method("set_auto_update_model", auto_update)
    
    def get_model_data(self):
        """获取模型数据"""
        return self.call_remote_method("get_model_data")
    
    def get_server_info(self):
        """获取服务器信息"""
        return self.call_remote_method("get_server_info")
    
    def clear_hda(self):
        """清除HDA"""
        return self.call_remote_method("clear_hda")
    
    def clear_temp_files(self):
        """清理服务器临时文件"""
        return self.call_remote_method("clear_temp_files")
    
    def ping_server(self):
        """Ping服务器"""
        try:
            if self.is_server_connected():
                # 尝试获取服务器信息来测试连接
                result = self.get_server_info()
                return result.get("success", False)
            return False
        except Exception:
            return False


class HoudiniConnectionManager(QObject):
    """Houdini连接管理器"""
    
    connection_status_changed = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self.client = HoudiniClient()
        self.ping_timer = QTimer()
        self.ping_timer.timeout.connect(self._ping_server)
        self.ping_interval = 30000  # 30秒ping一次
        
        # 连接信号
        self.client.connected.connect(self._on_connected)
        self.client.disconnected.connect(self._on_disconnected)
        self.client.connection_error.connect(self._on_connection_error)
    
    def _on_connected(self):
        """连接成功处理"""
        print("连接管理器：服务器连接成功")
        self.connection_status_changed.emit(True)
        self.ping_timer.start(self.ping_interval)
    
    def _on_disconnected(self):
        """断开连接处理"""
        print("连接管理器：服务器连接断开")
        self.connection_status_changed.emit(False)
        self.ping_timer.stop()
    
    def _on_connection_error(self, error_msg):
        """连接错误处理"""
        print(f"连接管理器：连接错误 - {error_msg}")
        self.connection_status_changed.emit(False)
        self.ping_timer.stop()
    
    def _ping_server(self):
        """定期ping服务器"""
        if not self.client.ping_server():
            print("服务器ping失败，尝试重连...")
            self.client.is_connected = False
            self._on_disconnected()
            # 尝试重连
            if self.client.settings.settings.get("auto_reconnect", True):
                self.client._schedule_reconnect()
    
    def connect_to_server(self, host=None, port=None):
        """连接到服务器"""
        self.client.connect_to_server(host, port)
    
    def disconnect(self):
        """断开连接"""
        self.client.disconnect()
    
    def is_connected(self):
        """检查连接状态"""
        return self.client.is_server_connected()
    
    def get_client(self):
        """获取客户端实例"""
        return self.client


# 全局连接管理器实例
_connection_manager = None

def get_connection_manager():
    """获取全局连接管理器实例"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = HoudiniConnectionManager()
    return _connection_manager 