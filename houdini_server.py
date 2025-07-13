#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Houdini Server
使用hrpyc提供远程HDA操作接口
注意：此代码运行在Houdini的Python环境中，不能使用第三方库
"""

import sys
import os
import argparse
import json
import time
import threading
import traceback
import tempfile
import shutil

def safe_str(obj):
    """安全地转换对象为字符串，避免Unicode编码错误"""
    try:
        result = str(obj)
        # 移除或替换可能的Unicode字符
        result = result.encode('ascii', errors='ignore').decode('ascii')
        return result
    except:
        return "未知错误"

def init_houdini_environment_for_server():
    """为服务器初始化Houdini环境"""
    # 如果已经在Houdini环境中，直接返回
    if 'hou' in sys.modules:
        return True, "Houdini环境已初始化"
    
    # 尝试从环境变量获取HFS路径
    hfs_path = os.environ.get("HFS")
    if not hfs_path:
        return False, "未设置HFS环境变量，请通过启动器启动服务器"
    
    # 使用重构后的init_houdini模块
    try:
        # 将panel/utils添加到路径中以便导入
        script_dir = os.path.dirname(os.path.abspath(__file__))
        panel_utils_path = os.path.join(script_dir, "panel", "utils")
        if panel_utils_path not in sys.path:
            sys.path.append(panel_utils_path)
        
        from init_houdini import init_houdini_server
        success, message = init_houdini_server(hfs_path)
        
        if success:
            print(f"Houdini环境初始化成功: {message}")
            return True, message
        else:
            print(f"Houdini环境初始化失败: {message}")
            return False, message
            
    except ImportError as e:
        # 如果无法导入init_houdini，尝试手动初始化
        print(f"无法导入init_houdini模块: {e}")
        print("尝试手动初始化Houdini环境...")
        
        try:
            # 手动设置环境变量
            if not os.environ.get("HHP"):
                # 查找Python库路径
                houdini_dir = os.path.join(hfs_path, "houdini")
                if os.path.exists(houdini_dir):
                    for item in os.listdir(houdini_dir):
                        if "python" in item.lower() and "libs" in item.lower():
                            pylib_path = os.path.join(houdini_dir, item)
                            if os.path.isdir(pylib_path) and "hou.py" in os.listdir(pylib_path):
                                os.environ["HHP"] = pylib_path
                                break
            
            # 添加到sys.path
            if os.environ.get("HHP") and os.environ["HHP"] not in sys.path:
                sys.path.append(os.environ["HHP"])
            
            # 尝试导入
            import hou
            import hrpyc
            print("手动初始化Houdini环境成功")
            return True, "手动初始化成功"
            
        except ImportError as e2:
            error_msg = f"无法导入Houdini模块: {e2}"
            print(error_msg)
            return False, error_msg

# 初始化Houdini环境
print("正在初始化Houdini环境...")
success, message = init_houdini_environment_for_server()
if not success:
    print(f"初始化失败: {message}")
    print("请确保：")
    print("1. 通过server_launcher.py启动服务器")
    print("2. 或者设置正确的HFS环境变量")
    sys.exit(1)

# 现在可以安全地导入Houdini模块
try:
    import hou
    import hrpyc
    print("Houdini模块导入成功")
except ImportError as e:
    print(f"导入Houdini模块失败: {e}")
    sys.exit(1)


class HoudiniServerSettings:
    """服务器设置管理"""
    
    def __init__(self, settings_file="server_settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
    
    def load_settings(self):
        """加载设置"""
        default_settings = {
            "server_host": "localhost",
            "server_port": 18811,
            "max_connections": 10,
            "timeout": 300,
            "debug": False
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # 合并默认设置
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception as e:
                print(f"加载设置失败: {e}")
        
        return default_settings
    
    def save_settings(self):
        """保存设置"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"保存设置失败: {e}")


class HoudiniRemoteService:
    """Houdini远程服务"""
    
    def __init__(self):
        self.current_hda_path = None
        self.current_hda_name = None
        self.current_hda_node = None
        self.current_hda_def = None
        self.node_parms = []
        self.auto_update_model = False
        self.last_model_update_time = 0
        self.model_update_interval = 0.005
        
        # 临时文件管理
        self.temp_dir = tempfile.mkdtemp(prefix="houdini_server_")
        self.temp_files = []  # 跟踪临时文件以便清理
        print(f"临时文件目录: {self.temp_dir}")
    
    def __del__(self):
        """析构函数，清理临时文件"""
        self.cleanup_temp_files()
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"已清理临时文件目录: {self.temp_dir}")
        except Exception as e:
            print(f"清理临时文件失败: {e}")
    
    def upload_file(self, file_data, filename):
        """上传文件到服务器临时目录 - 仅支持二进制数据"""
        try:
            # 创建临时文件路径
            temp_file_path = os.path.join(self.temp_dir, filename)
            
            # 确保目录存在
            temp_dir = os.path.dirname(temp_file_path)
            if temp_dir and not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
            
            # 只接受二进制数据
            if isinstance(file_data, str):
                raise Exception("不支持字符串数据，请使用二进制数据传输")
            
            # 验证是否为二进制数据
            if not isinstance(file_data, (bytes, bytearray)):
                raise Exception(f"无效的数据类型: {type(file_data)}, 需要二进制数据")
            
            # 写入文件
            with open(temp_file_path, 'wb') as f:
                f.write(file_data)
            
            # 验证文件完整性
            if not os.path.exists(temp_file_path):
                raise Exception("临时文件创建失败")
            
            file_size = os.path.getsize(temp_file_path)
            if file_size == 0:
                raise Exception("临时文件为空")
            
            # 记录临时文件
            self.temp_files.append(temp_file_path)
            
            print(f"文件上传成功: {filename} -> {temp_file_path} ({file_size} bytes)")
            
            return {
                "success": True,
                "message": "文件上传成功",
                "temp_path": temp_file_path,
                "original_filename": filename,
                "file_size": file_size
            }
            
        except Exception as e:
            error_str = safe_str(e)
            error_msg = f"文件上传失败: {error_str}"
            print(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "error": error_str
            }
    
    def clear_temp_files(self):
        """清理所有临时文件"""
        try:
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            self.temp_files.clear()
            
            return {"success": True, "message": "临时文件清理成功"}
        except Exception as e:
            error_msg = f"清理临时文件失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}

    def clear_hda(self):
        """清除当前HDA"""
        try:
            hou.hipFile.clear(suppress_save_prompt=True)
            self.current_hda_path = None
            self.current_hda_name = None
            self.current_hda_node = None
            self.current_hda_def = None
            self.node_parms = []
            return {"success": True, "message": "HDA清除成功"}
        except Exception as e:
            error_msg = f"清除HDA失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def load_hda(self, hda_path, hda_name=None):
        """加载HDA文件"""
        try:
            print(f"开始加载HDA: {hda_path}")
            
            # 检查文件是否存在
            if not os.path.exists(hda_path):
                error_msg = f"HDA文件不存在: {hda_path}"
                print(error_msg)
                return {"success": False, "message": error_msg}
            
            # 检查文件头部，确保是有效的HDA文件
            with open(hda_path, 'rb') as f:
                header = f.read(4)
                if header != b'INDX':
                    print(f"警告: 文件头部不是标准HDA格式: {header}")
                else:
                    print("HDA文件头部验证通过")
            
            # 清除现有场景
            print("清除现有场景...")
            self.clear_hda()
            
            # 加载HDA文件
            print(f"正在加载HDA文件: {hda_path}")
            hou.hda.installFile(hda_path)
            
            # 获取HDA定义
            hda_definitions = hou.hda.definitionsInFile(hda_path)
            if not hda_definitions:
                error_msg = f"HDA文件中没有找到有效的定义: {hda_path}"
                print(error_msg)
                return {"success": False, "message": error_msg}
            
            # 使用第一个定义
            hda_definition = hda_definitions[0]
            node_type = hda_definition.nodeType()
            
            print(f"找到HDA定义: {node_type.name()}")
            
            # 创建HDA节点
            if node_type.category().name() == "Sop":
                # SOP节点需要在geometry容器中创建
                geo_node = hou.node("/obj").createNode("geo", "hda_container")
                geo_node.children()[0].destroy()  # 删除默认的file节点
                hda_node = geo_node.createNode(node_type.name(), hda_name or "hda_node")
            else:
                # 其他类型的节点
                hda_node = hou.node("/obj").createNode(node_type.name(), hda_name or "hda_node")
            
            self.hda_node = hda_node
            self.hda_definition = hda_definition
            
            print(f"HDA节点创建成功: {hda_node.path()}")
            
            # 提取参数信息
            self._extract_node_parameters()
            
            # 设置布局
            if hasattr(hda_node.parent(), 'layoutChildren'):
                hda_node.parent().layoutChildren()
            
            print(f"HDA加载完成: {hda_node.path()}")
            
            return {
                "success": True, 
                "message": f"HDA加载成功: {hda_node.path()}",
                "node_path": hda_node.path(),
                "node_type": node_type.name(),
                "parameter_count": len(self.parameters)
            }
            
        except Exception as e:
            import traceback
            error_str = safe_str(e)
            error_msg = f"加载HDA失败: {error_str}"
            print(error_msg)
            print("错误详情:")
            traceback.print_exc()
            return {"success": False, "message": error_msg, "error": error_str, "error_type": type(e).__name__}
    
    def _extract_node_parameters(self):
        """提取节点参数信息"""
        if not self.current_hda_node:
            return []
        
        parameters = []
        
        try:
            for parm_tuple in self.current_hda_node.parmTuples():
                parm_template = parm_tuple.parmTemplate()
                parm_info = {
                    "name": parm_tuple.name(),
                    "label": parm_template.label(),
                    "type": self._get_parameter_type(parm_template),
                    "value": self._get_parameter_value(parm_tuple),
                    "help": parm_template.help() if hasattr(parm_template, 'help') else "",
                    "range": self._get_parameter_range(parm_template),
                    "options": self._get_parameter_options(parm_template)
                }
                parameters.append(parm_info)
                
        except Exception as e:
            print(f"提取参数信息失败: {e}")
        
        return parameters
    
    def _get_parameter_type(self, parm_template):
        """获取参数类型"""
        if isinstance(parm_template, hou.StringParmTemplate):
            if parm_template.stringType() == hou.stringParmType.FileReference:
                return "FILE_STRING"
            else:
                return "STRING"
        elif isinstance(parm_template, hou.FloatParmTemplate):
            if parm_template.numComponents() == 1:
                return "FLOAT"
            else:
                # 检查是否是颜色参数
                if parm_template.namingScheme() == hou.parmNamingScheme.RGBA:
                    return "COLOR"
                else:
                    return "FLOAT_ARRAY"
        elif isinstance(parm_template, hou.IntParmTemplate):
            if parm_template.numComponents() == 1:
                return "INT"
            else:
                return "INT_ARRAY"
        elif isinstance(parm_template, hou.ToggleParmTemplate):
            return "TOGGLE"
        elif isinstance(parm_template, hou.ButtonParmTemplate):
            return "BUTTON"
        elif isinstance(parm_template, hou.MenuParmTemplate):
            return "COMBOX"
        elif isinstance(parm_template, hou.RampParmTemplate):
            return "RAMP"
        else:
            return "UNKNOWN"
    
    def _get_parameter_value(self, parm_tuple):
        """获取参数值"""
        try:
            if len(parm_tuple) == 1:
                return parm_tuple[0].eval()
            else:
                return [parm.eval() for parm in parm_tuple]
        except Exception as e:
            print(f"获取参数值失败: {e}")
            return None
    
    def _get_parameter_range(self, parm_template):
        """获取参数范围"""
        try:
            if hasattr(parm_template, 'minValue') and hasattr(parm_template, 'maxValue'):
                return [parm_template.minValue(), parm_template.maxValue()]
        except Exception:
            pass
        return None
    
    def _get_parameter_options(self, parm_template):
        """获取参数选项（用于下拉菜单等）"""
        try:
            if isinstance(parm_template, hou.MenuParmTemplate):
                return {
                    "items": parm_template.menuItems(),
                    "labels": parm_template.menuLabels()
                }
        except Exception:
            pass
        return None
    
    def set_parameter(self, parm_name, value):
        """设置参数值"""
        if not self.current_hda_node:
            return {"success": False, "message": "没有加载的HDA节点"}
        
        try:
            parm_tuple = self.current_hda_node.parmTuple(parm_name)
            if not parm_tuple:
                return {"success": False, "message": f"参数不存在: {parm_name}"}
            
            # 根据参数类型设置值
            parm_template = parm_tuple.parmTemplate()
            
            if isinstance(parm_template, hou.ButtonParmTemplate):
                # 按钮参数需要按压
                parm_tuple[0].pressButton()
            elif isinstance(parm_template, hou.RampParmTemplate):
                # Ramp参数需要特殊处理
                if isinstance(value, dict) and "keys" in value and "values" in value:
                    # 处理 basis 参数 - 将字符串名称转换为 hou.rampBasis 对象
                    basis_list = value.get("basis", [])
                    converted_basis = []
                    
                    for basis_item in basis_list:
                        if isinstance(basis_item, str):
                            # 字符串名称转换为 hou.rampBasis 对象
                            if basis_item == "Constant":
                                converted_basis.append(hou.rampBasis.Constant)
                            elif basis_item == "Linear":
                                converted_basis.append(hou.rampBasis.Linear)
                            elif basis_item == "CatmullRom":
                                converted_basis.append(hou.rampBasis.CatmullRom)
                            elif basis_item == "MonotoneCubic":
                                converted_basis.append(hou.rampBasis.MonotoneCubic)
                            elif basis_item == "Bezier":
                                converted_basis.append(hou.rampBasis.Bezier)
                            elif basis_item == "BSpline":
                                converted_basis.append(hou.rampBasis.BSpline)
                            else:
                                converted_basis.append(hou.rampBasis.Linear)  # 默认
                        elif isinstance(basis_item, int):
                            # 整数值转换为 hou.rampBasis 对象
                            if basis_item == 0:
                                converted_basis.append(hou.rampBasis.Constant)
                            elif basis_item == 1:
                                converted_basis.append(hou.rampBasis.Linear)
                            elif basis_item == 2:
                                converted_basis.append(hou.rampBasis.CatmullRom)
                            elif basis_item == 3:
                                converted_basis.append(hou.rampBasis.MonotoneCubic)
                            elif basis_item == 4:
                                converted_basis.append(hou.rampBasis.Bezier)
                            elif basis_item == 5:
                                converted_basis.append(hou.rampBasis.BSpline)
                            else:
                                converted_basis.append(hou.rampBasis.Linear)  # 默认
                        else:
                            # 如果已经是 hou.rampBasis 对象，直接使用
                            converted_basis.append(basis_item)
                    
                    print(f"服务器端 RAMP 参数转换: {parm_name}")
                    print(f"  原始 basis: {basis_list}")
                    print(f"  转换后 basis: {converted_basis}")
                    
                    ramp = hou.Ramp(converted_basis, value["keys"], value["values"])
                    parm_tuple[0].set(ramp)
                else:
                    return {"success": False, "message": "Ramp参数格式错误"}
            elif len(parm_tuple) == 1:
                # 单个参数
                parm_tuple[0].set(value)
            else:
                # 多个参数（向量等）
                if isinstance(value, (list, tuple)):
                    parm_tuple.set(value)
                else:
                    return {"success": False, "message": "多维参数需要列表或元组值"}
            
            # 更新模型（如果启用）
            if self.auto_update_model:
                self._update_model()
            
            return {"success": True, "message": "参数设置成功"}
            
        except Exception as e:
            error_msg = f"设置参数失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def set_parameters(self, parameters):
        """批量设置参数"""
        if not self.current_hda_node:
            return {"success": False, "message": "没有加载的HDA节点"}
        
        try:
            # 暂停更新模式
            hou.setUpdateMode(hou.updateMode.Manual)
            
            results = []
            for parm_name, value in parameters.items():
                result = self.set_parameter(parm_name, value)
                results.append({"parameter": parm_name, "result": result})
            
            # 重新计算节点
            self.current_hda_node.cook()
            
            # 恢复更新模式
            hou.setUpdateMode(hou.updateMode.AutoUpdate)
            
            # 更新模型
            if self.auto_update_model:
                self._update_model()
            
            return {"success": True, "message": "批量参数设置完成", "results": results}
            
        except Exception as e:
            # 确保恢复更新模式
            hou.setUpdateMode(hou.updateMode.AutoUpdate)
            error_msg = f"批量设置参数失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def get_parameter(self, parm_name):
        """获取参数值"""
        if not self.current_hda_node:
            return {"success": False, "message": "没有加载的HDA节点"}
        
        try:
            parm_tuple = self.current_hda_node.parmTuple(parm_name)
            if not parm_tuple:
                return {"success": False, "message": f"参数不存在: {parm_name}"}
            
            value = self._get_parameter_value(parm_tuple)
            return {"success": True, "value": value}
            
        except Exception as e:
            error_msg = f"获取参数失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def get_all_parameters(self):
        """获取所有参数"""
        if not self.current_hda_node:
            return {"success": False, "message": "没有加载的HDA节点"}
        
        try:
            parameters = self._extract_node_parameters()
            return {"success": True, "parameters": parameters}
        except Exception as e:
            error_msg = f"获取所有参数失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def save_hip(self, file_path):
        """保存HIP文件"""
        try:
            hou.hipFile.save(file_path)
            return {"success": True, "message": f"HIP文件保存成功: {file_path}"}
        except Exception as e:
            error_msg = f"保存HIP文件失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def set_auto_update_model(self, auto_update):
        """设置自动更新模型"""
        self.auto_update_model = bool(auto_update)
        return {"success": True, "message": f"自动更新模型设置为: {self.auto_update_model}"}
    
    def _update_model(self):
        """更新模型"""
        if not self.auto_update_model or not self.current_hda_node:
            return
        
        current_time = time.time()
        if current_time - self.last_model_update_time < self.model_update_interval:
            return
        
        try:
            # 获取几何体数据
            geometry = self.current_hda_node.geometry()
            if geometry:
                vertices = []
                faces = []
                vertex_colors = []
                
                # 提取顶点和面
                for prim in geometry.prims():
                    if isinstance(prim, hou.Polygon):
                        face = []
                        for vertex in prim.vertices():
                            point = vertex.point()
                            pos = point.position()
                            vertices.append([pos.x(), pos.y(), pos.z()])
                            face.append(len(vertices) - 1)
                            
                            # 尝试获取颜色属性
                            try:
                                color_attrib = point.attribValue("Cd")
                                if color_attrib:
                                    if isinstance(color_attrib, (list, tuple)):
                                        vertex_colors.append(color_attrib[:3])
                                    else:
                                        vertex_colors.append([1.0, 1.0, 1.0])
                                else:
                                    vertex_colors.append([1.0, 1.0, 1.0])
                            except:
                                vertex_colors.append([1.0, 1.0, 1.0])
                        
                        faces.append(face)
                
                self.last_model_update_time = current_time
                return {
                    "vertices": vertices,
                    "faces": faces,
                    "vertex_colors": vertex_colors
                }
        except Exception as e:
            print(f"更新模型失败: {e}")
            return None
    
    def get_model_data(self):
        """获取模型数据"""
        try:
            model_data = self._update_model()
            if model_data is not None:
                return {
                    "success": True,
                    "vertices": model_data.get("vertices", []),
                    "faces": model_data.get("faces", []),
                    "vertex_colors": model_data.get("vertex_colors", [])
                }
            else:
                return {"success": False, "message": "没有可用的模型数据"}
        except Exception as e:
            error_msg = f"获取模型数据失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}
    
    def get_server_info(self):
        """获取服务器信息"""
        try:
            return {
                "success": True,
                "houdini_version": hou.applicationVersionString(),
                "current_hda": self.current_hda_name,
                "current_hda_path": self.current_hda_path,
                "node_path": self.current_hda_node.path() if self.current_hda_node else None,
                "auto_update_model": self.auto_update_model
            }
        except Exception as e:
            error_msg = f"获取服务器信息失败: {str(e)}"
            print(error_msg)
            return {"success": False, "message": error_msg, "error": str(e)}


class HoudiniServer:
    """Houdini服务器主类"""
    
    def __init__(self, host="localhost", port=18811):
        self.host = host
        self.port = port
        self.settings = HoudiniServerSettings()
        self.service = HoudiniRemoteService()
        self.server_thread = None
        self.running = False
    
    def start(self):
        """启动服务器"""
        try:
            # 先导入hou模块
            import hou
            
            print(f"正在启动Houdini服务器...")
            print(f"地址: {self.host}:{self.port}")
            print(f"Houdini版本: {hou.applicationVersionString()}")
            
            # 启动hrpyc服务器
            # 注意：hrpyc.start_server()不支持host参数，只能监听localhost
            if self.host != "localhost" and self.host != "127.0.0.1":
                print(f"警告：hrpyc只支持监听localhost，忽略host参数: {self.host}")
            
            hrpyc.start_server(port=self.port)
            
            # 将服务注册到hou模块，这样客户端就能通过hou.houdini_service访问
            hou.houdini_service = self.service
            
            # 同时也注册到__main__作为备用
            import __main__
            __main__.houdini_service = self.service
            
            self.running = True
            print("服务器启动成功！")
            print("可用的远程方法:")
            print("  - houdini_service.upload_file(file_data, filename)")
            print("  - houdini_service.load_hda(hda_path, hda_name)")
            print("  - houdini_service.set_parameter(parm_name, value)")
            print("  - houdini_service.set_parameters(parameters)")
            print("  - houdini_service.get_parameter(parm_name)")
            print("  - houdini_service.get_all_parameters()")
            print("  - houdini_service.save_hip(file_path)")
            print("  - houdini_service.set_auto_update_model(auto_update)")
            print("  - houdini_service.get_model_data()")
            print("  - houdini_service.get_server_info()")
            print("  - houdini_service.clear_hda()")
            print("  - houdini_service.clear_temp_files()")
            
            return True
            
        except Exception as e:
            print(f"启动服务器失败: {e}")
            traceback.print_exc()
            return False
    
    def stop(self):
        """停止服务器"""
        try:
            self.running = False
            print("服务器已停止")
            return True
        except Exception as e:
            print(f"停止服务器失败: {e}")
            return False
    
    def run_forever(self):
        """保持服务器运行"""
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到中断信号，正在停止服务器...")
            self.stop()


def main():
    parser = argparse.ArgumentParser(description="Houdini RPC服务器")
    parser.add_argument("--host", default="localhost", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=18811, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    
    args = parser.parse_args()
    
    # 创建并启动服务器
    server = HoudiniServer(host=args.host, port=args.port)
    
    if server.start():
        try:
            server.run_forever()
        except KeyboardInterrupt:
            print("\n正在关闭服务器...")
            server.stop()
    else:
        print("服务器启动失败")
        sys.exit(1)


if __name__ == "__main__":
    main() 