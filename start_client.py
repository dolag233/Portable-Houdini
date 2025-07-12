#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
客户端启动脚本
确保使用正确的Python环境
"""

import os
import sys
import subprocess
from pathlib import Path

def find_python_executable():
    """查找合适的Python可执行文件"""
    current_dir = Path(__file__).parent
    
    # 检查是否在venv环境中
    venv_path = current_dir / "venv"
    if venv_path.exists():
        # 检查标准虚拟环境结构
        if os.name == 'nt':
            venv_python = venv_path / "Scripts" / "python.exe"
        else:
            venv_python = venv_path / "bin" / "python"
        
        if venv_python.exists():
            print(f"使用虚拟环境Python: {venv_python}")
            return str(venv_python)
        
        # 检查项目特定的Python结构
        python39_path = venv_path / "Python39" / "python.exe"
        if python39_path.exists():
            print(f"使用项目Python39: {python39_path}")
            return str(python39_path)
            
        python37_path = venv_path / "Python37" / "python.exe"
        if python37_path.exists():
            print(f"使用项目Python37: {python37_path}")
            return str(python37_path)
    
    # 使用当前Python
    print(f"使用当前Python: {sys.executable}")
    return sys.executable

def main():
    """主函数"""
    print("=== Portable Houdini 客户端启动器 ===")
    
    # 查找Python可执行文件
    python_exe = find_python_executable()
    
    # 设置环境变量
    env = os.environ.copy()
    
    # 启动主程序
    main_script = Path(__file__).parent / "main.py"
    
    try:
        print(f"启动客户端: {python_exe} {main_script}")
        
        # 使用subprocess启动，这样可以传递环境变量
        result = subprocess.run([python_exe, str(main_script)], env=env)
        
        return result.returncode
        
    except Exception as e:
        print(f"启动客户端失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 