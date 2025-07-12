#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试远程连接
"""

import sys
import os
import time
import subprocess
from pathlib import Path

def test_remote_connection():
    """测试远程连接"""
    print("=== 测试远程连接 ===")
    
    # 检查venv环境
    venv_path = Path(__file__).parent / "venv"
    if venv_path.exists():
        # 检查标准虚拟环境结构
        if os.name == 'nt':
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        if python_exe.exists():
            print(f"使用虚拟环境Python: {python_exe}")
        else:
            # 检查项目特定的Python结构
            python39_path = venv_path / "Python39" / "python.exe"
            if python39_path.exists():
                python_exe = python39_path
                print(f"使用项目Python39: {python_exe}")
            else:
                python37_path = venv_path / "Python37" / "python.exe"
                if python37_path.exists():
                    python_exe = python37_path
                    print(f"使用项目Python37: {python_exe}")
                else:
                    python_exe = sys.executable
                    print(f"虚拟环境Python不存在，使用当前Python: {python_exe}")
    else:
        python_exe = sys.executable
        print(f"未找到虚拟环境，使用当前Python: {python_exe}")
    
    # 测试hrpyc连接
    test_script = """
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'panel'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'panel', 'utils'))

try:
    print("正在导入hrpyc...")
    import hrpyc
    
    print("正在连接到服务器...")
    connection, hou = hrpyc.import_remote_module()
    
    print("连接成功！")
    print(f"hou模块: {hou}")
    
    # 检查houdini_service是否存在
    if hasattr(hou, 'houdini_service'):
        print("[OK] 找到 hou.houdini_service")
        service = hou.houdini_service
        
        # 测试获取服务器信息
        info = service.get_server_info()
        print(f"[OK] 服务器信息: {info}")
        
    else:
        print("[ERROR] 未找到 hou.houdini_service")
        print(f"hou模块属性: {dir(hou)}")
    
    connection.close()
    print("连接已关闭")
    
except Exception as e:
    print(f"连接失败: {e}")
    import traceback
    traceback.print_exc()
"""
    
    # 创建临时测试文件
    test_file = Path(__file__).parent / "temp_test_connection.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    try:
        # 运行测试
        result = subprocess.run([str(python_exe), str(test_file)], 
                              capture_output=True, text=True, timeout=30)
        
        print("=== 测试输出 ===")
        print(result.stdout)
        
        if result.stderr:
            print("=== 错误输出 ===")
            print(result.stderr)
        
        print(f"返回码: {result.returncode}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("测试超时")
        return False
    except Exception as e:
        print(f"测试失败: {e}")
        return False
    finally:
        # 清理临时文件
        if test_file.exists():
            test_file.unlink()

def main():
    """主函数"""
    success = test_remote_connection()
    
    if success:
        print("\n[SUCCESS] 远程连接测试成功！")
    else:
        print("\n[FAILED] 远程连接测试失败！")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 