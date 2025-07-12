import os
import sys
import platform

# 保存原始PATH
os_path = os.environ.get("PATH", "")

def init_houdini_environment(houdini_path=None, settings_manager=None, show_gui_error=True):
    """
    初始化 Houdini 环境
    
    Args:
        houdini_path: Houdini 安装路径，如果为 None 则从设置中获取
        settings_manager: 设置管理器实例，用于获取 Houdini 路径
        show_gui_error: 是否显示 GUI 错误对话框
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    if 'hou' in sys.modules:
        return True, "Houdini 环境已初始化"
    
    print("正在初始化 Houdini 环境...")
    
    # 获取 Houdini 路径
    if houdini_path is None:
        if settings_manager is None:
            return False, "未提供 Houdini 路径或设置管理器"
        
        try:
            from settings_manager import SettingsEnum
            houdini_path = settings_manager.get(SettingsEnum.HOUDINI_PATH)
        except ImportError:
            return False, "无法导入设置管理器"
    
    # 验证 Houdini 路径
    if not houdini_path or not os.path.isdir(houdini_path):
        error_msg = f"无效的 Houdini 路径: {houdini_path}"
        if show_gui_error:
            _show_gui_error(error_msg)
        return False, error_msg
    
    if not os.path.isdir(os.path.join(houdini_path, "houdini")):
        error_msg = f"Houdini 路径中未找到 houdini 目录: {houdini_path}"
        if show_gui_error:
            _show_gui_error(error_msg)
        return False, error_msg
    
    # 查找 Python 库路径
    pylib_path = _find_houdini_pylib(houdini_path)
    if not pylib_path:
        error_msg = f"在 Houdini 路径中未找到 Python 库: {houdini_path}"
        if show_gui_error:
            _show_gui_error(error_msg)
        return False, error_msg
    
    # 设置环境变量
    os.environ["HHP"] = pylib_path
    os.environ["HFS"] = houdini_path
    os.environ["PATH"] = f"{houdini_path}/bin;{pylib_path};" + os.environ.get("PATH", "")
    
    # 准备 Houdini 环境
    old_dlopen_flags = None
    if hasattr(sys, "setdlopenflags"):
        old_dlopen_flags = sys.getdlopenflags()
        sys.setdlopenflags(old_dlopen_flags | os.RTLD_GLOBAL)
    
    if sys.platform == "win32" and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(f"{houdini_path}/bin")
    
    try:
        import hou
        print("Houdini 环境初始化成功！")
        return True, "Houdini 环境初始化成功"
    except ImportError:
        try:
            sys.path.append(pylib_path)
            import hou
            print("Houdini 环境初始化成功！")
            return True, "Houdini 环境初始化成功"
        except ImportError as e:
            error_msg = f"无法导入 Houdini 模块: {e}"
            if show_gui_error:
                _show_gui_error(error_msg)
            return False, error_msg
    finally:
        if old_dlopen_flags is not None and hasattr(sys, "setdlopenflags"):
            sys.setdlopenflags(old_dlopen_flags)
        
        # 恢复原始 PATH
        if os_path:
            os.environ["PATH"] += ";" + os_path


def init_houdini_server(houdini_path):
    """
    专门用于服务器端的 Houdini 环境初始化
    
    Args:
        houdini_path: Houdini 安装路径
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    return init_houdini_environment(houdini_path=houdini_path, show_gui_error=False)


def _find_houdini_pylib(houdini_path):
    """查找 Houdini Python 库路径"""
    houdini_dir = os.path.join(houdini_path, "houdini")
    if not os.path.exists(houdini_dir):
        return None
    
    # 查找包含 hou.py 的 Python 库目录
    for item in os.listdir(houdini_dir):
        if "python" in item.lower() and "libs" in item.lower():
            pylib_path = os.path.join(houdini_dir, item)
            if os.path.isdir(pylib_path) and "hou.py" in os.listdir(pylib_path):
                return pylib_path
    
    return None


def _show_gui_error(error_message):
    """显示 GUI 错误对话框（仅在客户端使用）"""
    try:
        from localization import LANG_STR_ENUM, getLocalizationStr
        from PySide2.QtWidgets import QApplication, QMessageBox
        
        msg_box = QMessageBox(QMessageBox.Warning, 
                            getLocalizationStr(LANG_STR_ENUM.ERROR_HOU_PATH),
                            error_message)
        msg_box.exec_()
    except ImportError:
        # 如果无法导入 GUI 组件，则只打印错误
        print(f"Houdini 初始化错误: {error_message}")


# 向后兼容：保持原有的客户端初始化行为
if __name__ == "__main__" or 'hou' not in sys.modules:
    try:
        from settings_manager import SettingsEnum
        from globals import SETTINGS_MANAGER
        
        success, message = init_houdini_environment(settings_manager=SETTINGS_MANAGER)
        if not success:
            raise ImportError(message)
    except ImportError as e:
        print(f"Houdini 环境初始化失败: {e}")
        # 在客户端环境中，这会触发 GUI 错误对话框
        if 'QApplication' in sys.modules:
            raise
