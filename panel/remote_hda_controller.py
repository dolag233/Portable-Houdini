#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Remote HDA Controller
仅支持远程模式的HDA控制器
"""

import sys
import os
import time
import threading
from queue import Queue
from PySide2.QtCore import QTimer, Qt, Signal, QObject, QThread

from hou_parms_model import HouParamMetaEnum, HouParamTypeEnum
from utils.globals import APP
from qwidget.qt_progress_bar import QProgressBarWidget
from utils.houdini_client import get_connection_manager


class RemoteHDAController(QObject):
    """远程HDA控制器 - 仅支持远程模式"""
    
    # 信号定义
    cook_started = Signal()
    cook_finished = Signal()
    update_display_model = Signal(list, list, list)  # [vertices, vertex_colors, faces]
    connection_status_changed = Signal(bool)
    server_error = Signal(str)
    
    def __init__(self, model):
        super().__init__()
        self._model = model
        self._connection_manager = get_connection_manager()
        self._mode = "remote"  # 仅支持远程模式
        
        # 远程模式相关
        self._remote_client = None
        
        # 当前HDA信息
        self._current_hda_path = None
        self._current_hda_name = None
        self._current_hip_path = None
        self._current_hip_name = None
        self._auto_update_model = False
        self._last_model_update_time = 0
        self._model_update_interval = 0.005
        
        # 队列处理
        self.queue = Queue()
        self.worker_thread = threading.Thread(target=self.processQueue)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        # 连接信号
        self._model.view_data_changed.connect(self.queueWriteHDAProperty)
        self._model.view_datas_changed.connect(self.queueWriteHDAProperties)
        self._connection_manager.connection_status_changed.connect(self._on_connection_status_changed)
        
        self._last_model_update_time = time.time()
        
        # 初始化远程模式
        self._setup_remote_mode()
    
    def set_mode(self, mode):
        """设置工作模式 - 仅支持远程模式"""
        if mode != "remote":
            print(f"警告：客户端仅支持远程模式，忽略模式设置: {mode}")
            return
        
        self._mode = "remote"
        self._setup_remote_mode()
    
    def _setup_remote_mode(self):
        """设置远程模式"""
        self._remote_client = self._connection_manager.get_client()
        if self._remote_client:
            # 连接远程客户端的信号
            self._remote_client.server_response.connect(self._on_server_response)
            print("远程模式设置完成")
            return True
        return False
    
    def _on_connection_status_changed(self, connected):
        """连接状态变化处理"""
        self.connection_status_changed.emit(connected)
        if connected:
            print("远程服务器连接成功")
        else:
            print("远程服务器连接断开")
    
    def _on_server_response(self, response):
        """服务器响应处理"""
        method = response.get("method", "")
        result = response.get("result", {})
        
        if method in ["set_parameter", "set_parameters"]:
            # 参数设置响应
            if result.get("success", False):
                self.cook_finished.emit()
                # 更新模型
                if self._auto_update_model:
                    self._update_remote_model()
            else:
                self.server_error.emit(result.get("message", "未知错误"))
        elif method == "get_model_data":
            # 模型数据响应
            if result:
                vertices = result.get("vertices", [])
                faces = result.get("faces", [])
                vertex_colors = result.get("vertex_colors", [])
                self.update_display_model.emit(vertices, vertex_colors, faces)
    
    def connect_to_server(self, host="localhost", port=18811):
        """连接到远程服务器"""
        self._connection_manager.connect_to_server(host, port)
        return True
    
    def disconnect_from_server(self):
        """断开服务器连接"""
        self._connection_manager.disconnect()
    
    def is_connected(self):
        """检查是否连接到服务器"""
        return self._connection_manager.is_connected()
    
    def get_mode(self):
        """获取当前模式"""
        return self._mode
    
    # 队列处理方法
    def queueWriteHDAProperty(self, parm_meta):
        """队列写入HDA属性"""
        parm_meta_data = {
            'type': parm_meta.getData(HouParamMetaEnum.TYPE),
            'name': parm_meta.getData(HouParamMetaEnum.NAME),
            'parm_tuple_ref': parm_meta.getData(HouParamMetaEnum.PARM_TUPLE_REF),
            'value': parm_meta.getData(HouParamMetaEnum.VALUE)
        }
        self.queue.put(("parm", parm_meta_data))
    
    def queueWriteHDAProperties(self, parm_metas):
        """队列写入多个HDA属性"""
        parm_metas_data = []
        for parm_meta in parm_metas:
            parm_meta_data = {
                'type': parm_meta.getData(HouParamMetaEnum.TYPE),
                'name': parm_meta.getData(HouParamMetaEnum.NAME),
                'parm_tuple_ref': parm_meta.getData(HouParamMetaEnum.PARM_TUPLE_REF),
                'value': parm_meta.getData(HouParamMetaEnum.VALUE)
            }
            parm_metas_data.append(parm_meta_data)
        self.queue.put(("parms", parm_metas_data))
    
    def processQueue(self):
        """处理队列"""
        while True:
            if self.queue.empty():
                time.sleep(0.5)
                continue
            else:
                process_type, parm_data = self.queue.get()
                if process_type == "parm":
                    self.writeHDAProperty(parm_data)
                elif process_type == "parms":
                    self.writeHDAProperties(parm_data)
                self.queue.task_done()
    
    def writeHDAProperty(self, parm_meta_data):
        """写入HDA属性"""
        self._write_remote_property(parm_meta_data)
    
    def writeHDAProperties(self, parm_metas_data):
        """写入多个HDA属性"""
        self._write_remote_properties(parm_metas_data)
    
    def _write_remote_property(self, parm_meta_data):
        """远程模式写入属性"""
        if not self.is_connected():
            print("未连接到远程服务器")
            return
        
        self.cook_started.emit()
        
        parm_name = parm_meta_data['name']
        parm_value = parm_meta_data['value']
        parm_type = parm_meta_data['type']
        
        # 特殊处理 RAMP 参数 - 转换 hou.EnumValue 对象
        if parm_type == HouParamTypeEnum.RAMP and isinstance(parm_value, dict):
            print(f"=== RAMP 参数调试信息 ===")
            print(f"参数名: {parm_name}")
            print(f"参数类型: {parm_type}")
            print(f"参数值类型: {type(parm_value)}")
            print(f"原始参数值: {parm_value}")
            
            # 转换 basis 数组中的 hou.EnumValue 对象
            if 'basis' in parm_value:
                basis_list = parm_value['basis']
                converted_basis = []
                
                print(f"原始 basis: {basis_list}")
                print(f"basis 类型: {type(basis_list)}")
                print(f"basis 长度: {len(basis_list)}")
                
                for i, basis_item in enumerate(basis_list):
                    print(f"basis[{i}]: {basis_item} (类型: {type(basis_item)})")
                    
                    try:
                        # 如果是 hou.EnumValue 对象，转换为字符串名称
                        if hasattr(basis_item, 'name'):
                            # 提取名称部分，如 "rampBasis.Linear" -> "Linear"
                            name = str(basis_item.name)
                            if 'Constant' in name:
                                converted_basis.append("Constant")
                                print(f"  -> 名称映射: Constant")
                            elif 'Linear' in name:
                                converted_basis.append("Linear")
                                print(f"  -> 名称映射: Linear")
                            elif 'CatmullRom' in name:
                                converted_basis.append("CatmullRom")
                                print(f"  -> 名称映射: CatmullRom")
                            elif 'MonotoneCubic' in name:
                                converted_basis.append("MonotoneCubic")
                                print(f"  -> 名称映射: MonotoneCubic")
                            elif 'Bezier' in name:
                                converted_basis.append("Bezier")
                                print(f"  -> 名称映射: Bezier")
                            elif 'BSpline' in name:
                                converted_basis.append("BSpline")
                                print(f"  -> 名称映射: BSpline")
                            else:
                                converted_basis.append("Linear")  # 默认 Linear
                                print(f"  -> 未知名称，使用默认: Linear")
                        elif hasattr(basis_item, 'value'):
                            # 如果有 value 属性，通过整数值映射
                            basis_value = int(basis_item.value)
                            if basis_value == 0:
                                converted_basis.append("Constant")
                                print(f"  -> 整数映射: Constant")
                            elif basis_value == 1:
                                converted_basis.append("Linear")
                                print(f"  -> 整数映射: Linear")
                            elif basis_value == 2:
                                converted_basis.append("CatmullRom")
                                print(f"  -> 整数映射: CatmullRom")
                            elif basis_value == 3:
                                converted_basis.append("MonotoneCubic")
                                print(f"  -> 整数映射: MonotoneCubic")
                            elif basis_value == 4:
                                converted_basis.append("Bezier")
                                print(f"  -> 整数映射: Bezier")
                            elif basis_value == 5:
                                converted_basis.append("BSpline")
                                print(f"  -> 整数映射: BSpline")
                            else:
                                converted_basis.append("Linear")
                                print(f"  -> 未知整数值，使用默认: Linear")
                        else:
                            # 如果已经是字符串，直接使用
                            converted_basis.append(str(basis_item))
                            print(f"  -> 直接使用字符串: {str(basis_item)}")
                    except Exception as e:
                        print(f"  -> 转换 basis 项时出错: {e}, 使用默认值: Linear")
                        converted_basis.append("Linear")
                
                # 更新参数值
                parm_value = parm_value.copy()  # 创建副本避免修改原始数据
                parm_value['basis'] = converted_basis
                
                print(f"转换后的 basis: {converted_basis}")
                print(f"最终参数值: {parm_value}")
            
            print(f"=== 调试信息结束 ===")
        
        # 调用远程方法
        result = self._remote_client.set_parameter(parm_name, parm_value)
        
        if not result.get("success", False):
            error_msg = result.get("message", "设置参数失败")
            print(f"设置参数失败: {error_msg}")
            self.server_error.emit(error_msg)
    
    def _write_remote_properties(self, parm_metas_data):
        """远程模式写入多个属性"""
        if not self.is_connected():
            print("未连接到远程服务器")
            return
        
        self.cook_started.emit()
        
        # 构建参数字典
        parameters = {}
        for parm_meta_data in parm_metas_data:
            parm_name = parm_meta_data['name']
            parm_value = parm_meta_data['value']
            parameters[parm_name] = parm_value
        
        # 调用远程方法
        result = self._remote_client.set_parameters(parameters)
        
        if not result.get("success", False):
            self.server_error.emit(result.get("message", "批量设置参数失败"))
    
    # HDA操作方法
    def clearHDA(self):
        """清除HDA"""
        if self.is_connected():
            result = self._remote_client.clear_hda()
            if not result.get("success", False):
                self.server_error.emit(result.get("message", "清除HDA失败"))
    
    def loadHDA(self):
        """加载HDA"""
        print("远程控制器: 开始加载 HDA")
        
        if self.is_connected() and self._current_hda_path:
            print(f"远程控制器: 调用远程加载 HDA: {self._current_hda_path}")
            result = self._remote_client.load_hda(self._current_hda_path, self._current_hda_name)
            
            print(f"远程控制器: 服务器响应: {result}")
            
            if result.get("success", False):
                # 更新模型中的参数
                parameters = result.get("parameters", [])
                print(f"远程控制器: 收到 {len(parameters)} 个参数")
                
                if parameters:
                    print("远程控制器: 开始更新模型参数")
                    self._update_model_from_remote_parameters(parameters)
                    print("远程控制器: 模型参数更新完成")
                else:
                    print("远程控制器: 警告 - 没有收到任何参数数据")
                
                return True
            else:
                error_msg = result.get("message", "加载HDA失败")
                print(f"远程控制器: 错误 - {error_msg}")
                self.server_error.emit(error_msg)
                return False
        else:
            if not self.is_connected():
                print("远程控制器: 错误 - 未连接到服务器")
            if not self._current_hda_path:
                print("远程控制器: 错误 - 没有设置 HDA 路径")
            
        return False
    
    def _should_filter_parameter(self, parm_name):
        """判断是否应该过滤掉某个参数"""
        import re
        
        # 过滤 RAMP 控制点参数
        # 格式：ramp1pos, ramp1value, ramp1interp, ramp2pos, ramp2value, ramp2interp, 等等
        ramp_control_pattern = r'^ramp\d+(pos|value|interp)$'
        if re.match(ramp_control_pattern, parm_name):
            return True
        
        # 过滤 folder 参数 (通常是界面分组，不需要显示)
        if parm_name.startswith('folder') and parm_name[6:].isdigit():
            return True
        
        return False
    
    def _update_model_from_remote_parameters(self, parameters):
        """从远程参数更新模型"""
        if not self._model or not parameters:
            return
            
        # 清除现有参数
        self._model.clearHDA()
        
        # 导入必要的类型
        from hou_parms_model import HouParmMetadata, HouParamMetaEnum, HouParamTypeEnum, HouParmCombox
        
        print(f"正在处理 {len(parameters)} 个远程参数...")
        
        filtered_count = 0
        for param_info in parameters:
            try:
                # 创建参数元数据
                parm_meta = HouParmMetadata()
                
                # 获取参数基本信息
                parm_name = param_info.get("name", "")
                parm_label = param_info.get("label", "")
                parm_type_str = param_info.get("type", "")
                parm_value = param_info.get("value", None)
                parm_help = param_info.get("help", "")
                parm_range = param_info.get("range", None)
                parm_options = param_info.get("options", None)
                
                # 过滤不需要显示的参数
                if self._should_filter_parameter(parm_name):
                    filtered_count += 1
                    continue
                
                # 转换参数类型
                parm_type = self._convert_remote_type_to_local(parm_type_str)
                if parm_type is None:
                    print(f"警告: 未知的参数类型 {parm_type_str} for {parm_name}")
                    continue
                
                # 特殊处理 RAMP 参数 - 将 hou.Ramp 对象转换为字典
                if parm_type_str == "RAMP" and parm_value is not None:
                    try:
                        # 检查是否是 hou.Ramp 对象
                        if hasattr(parm_value, 'keys') and hasattr(parm_value, 'values') and hasattr(parm_value, 'basis'):
                            # 转换为字典格式
                            parm_value = {
                                'keys': list(parm_value.keys()),
                                'values': list(parm_value.values()),
                                'basis': list(parm_value.basis())
                            }
                            print(f"RAMP 参数转换: {parm_name} (包含 {len(parm_value['keys'])} 个控制点)")
                        elif isinstance(parm_value, dict) and 'basis' in parm_value:
                            # 如果已经是字典格式，转换 basis 数组中的 hou.EnumValue 对象
                            basis_list = parm_value.get('basis', [])
                            converted_basis = []
                            
                            for basis_item in basis_list:
                                try:
                                    # 如果是 hou.EnumValue 对象，转换为整数
                                    if hasattr(basis_item, 'value'):
                                        converted_basis.append(int(basis_item.value))
                                    elif hasattr(basis_item, 'name'):
                                        # 通过名称映射
                                        name = str(basis_item.name)
                                        if 'Constant' in name:
                                            converted_basis.append(0)
                                        elif 'Linear' in name:
                                            converted_basis.append(1)
                                        elif 'CatmullRom' in name:
                                            converted_basis.append(2)
                                        elif 'MonotoneCubic' in name:
                                            converted_basis.append(3)
                                        elif 'Bezier' in name:
                                            converted_basis.append(4)
                                        elif 'BSpline' in name:
                                            converted_basis.append(5)
                                        else:
                                            converted_basis.append(1)  # 默认 Linear
                                    else:
                                        # 如果已经是整数，直接使用
                                        converted_basis.append(int(basis_item))
                                except Exception as e:
                                    print(f"转换 basis 项时出错: {e}, 使用默认值 1 (Linear)")
                                    converted_basis.append(1)
                            
                            parm_value['basis'] = converted_basis
                            print(f"RAMP 参数 basis 转换: {parm_name} -> {converted_basis}")
                        else:
                            print(f"警告: RAMP 参数 {parm_name} 不是有效的 hou.Ramp 对象或字典")
                    except Exception as e:
                        print(f"警告: RAMP 参数 {parm_name} 转换失败: {e}")
                        continue
                
                # 设置基本数据
                parm_meta.setData(parm_name, parm_label, parm_type, parm_value, parm_help, None)
                
                # 设置范围信息
                if parm_range is not None:
                    parm_meta.setDataSpecific(HouParamMetaEnum.VALUE_RANGE, parm_range)
                
                # 设置下拉菜单选项
                if parm_options is not None and parm_type == HouParamTypeEnum.COMBOX:
                    parm_combox = HouParmCombox()
                    parm_combox.items = parm_options.get("items", [])
                    parm_combox.labels = parm_options.get("labels", [])
                    parm_meta.setDataSpecific(HouParamMetaEnum.COMBOX_DEFINE, parm_combox)
                
                # 添加到模型
                self._model.parms.append(parm_meta)
                print(f"添加参数: {parm_name} ({parm_type_str}) = {parm_value}")
                
            except Exception as e:
                print(f"处理参数 {param_info.get('name', 'unknown')} 时出错: {e}")
                continue
        
        print(f"成功添加 {len(self._model.parms)} 个参数到模型 (过滤了 {filtered_count} 个 RAMP 控制点和 folder 参数)")
    
    def _convert_remote_type_to_local(self, remote_type):
        """转换远程参数类型到本地类型"""
        from hou_parms_model import HouParamTypeEnum
        
        type_mapping = {
            "STRING": HouParamTypeEnum.STRING,
            "FILE_STRING": HouParamTypeEnum.FILE_STRING,
            "FLOAT": HouParamTypeEnum.FLOAT,
            "FLOAT_ARRAY": HouParamTypeEnum.FLOAT_ARRAY,
            "INT": HouParamTypeEnum.INT,
            "INT_ARRAY": HouParamTypeEnum.INT_ARRAY,
            "TOGGLE": HouParamTypeEnum.TOGGLE,
            "BUTTON": HouParamTypeEnum.BUTTON,
            "RAMP": HouParamTypeEnum.RAMP,
            "COMBOX": HouParamTypeEnum.COMBOX,
            "COLOR": HouParamTypeEnum.COLOR,
            # 添加小写版本以防万一
            "string": HouParamTypeEnum.STRING,
            "file_string": HouParamTypeEnum.FILE_STRING,
            "float": HouParamTypeEnum.FLOAT,
            "float_array": HouParamTypeEnum.FLOAT_ARRAY,
            "int": HouParamTypeEnum.INT,
            "int_array": HouParamTypeEnum.INT_ARRAY,
            "toggle": HouParamTypeEnum.TOGGLE,
            "button": HouParamTypeEnum.BUTTON,
            "ramp": HouParamTypeEnum.RAMP,
            "menu": HouParamTypeEnum.COMBOX,
            "color": HouParamTypeEnum.COLOR,
        }
        
        return type_mapping.get(remote_type, None)
    
    def saveHIP(self, file_path):
        """保存HIP文件"""
        if self.is_connected():
            result = self._remote_client.save_hip(file_path)
            if not result.get("success", False):
                self.server_error.emit(result.get("message", "保存HIP失败"))
    
    def setAutoUpdateModel(self, auto):
        """设置自动更新模型"""
        self._auto_update_model = bool(auto)
        
        if self.is_connected():
            result = self._remote_client.set_auto_update_model(auto)
            if not result.get("success", False):
                self.server_error.emit(result.get("message", "设置自动更新模型失败"))
    
    def updateNodeModel(self):
        """更新节点模型"""
        self._update_remote_model()
    
    def _update_remote_model(self):
        """更新远程模型"""
        if not self.is_connected():
            return
        
        current_time = time.time()
        if current_time - self._last_model_update_time < self._model_update_interval:
            return
        
        self._last_model_update_time = current_time
        
        # 获取远程模型数据
        self._remote_client.get_model_data()
    
    # 属性访问方法
    def getCurrentHDAPath(self):
        """获取当前HDA路径"""
        return self._current_hda_path
    
    def getCurrentHIPPath(self):
        """获取当前HIP路径"""
        return self._current_hip_path
    
    def setCurHDAPath(self, hda_path):
        """设置当前HDA路径"""
        self._current_hda_path = hda_path
    
    def setCurHDAName(self, hda_name):
        """设置当前HDA名称"""
        self._current_hda_name = hda_name
    
    def setCurHIPPath(self, hip_path):
        """设置当前HIP路径"""
        self._current_hip_path = hip_path
    
    def setCurHIPName(self, hip_name):
        """设置当前HIP名称"""
        self._current_hip_name = hip_name
    
    def checkValid(self):
        """检查是否有效"""
        return (self._current_hda_path is not None) or (self._current_hip_path is not None)
    
    def getCurNode(self):
        """获取当前节点"""
        return None  # 远程模式不返回实际节点对象
    
    def unloadHDA(self):
        """卸载HDA"""
        # 远程模式清除本地状态
        self._current_hda_path = None
        self._current_hda_name = None
        self._current_hip_path = None
        self._current_hip_name = None
    
    def get_server_info(self):
        """获取服务器信息"""
        if self.is_connected():
            return self._remote_client.get_server_info()
        return None 