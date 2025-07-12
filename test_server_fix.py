#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试服务器修复
"""

import os
import sys
import time
import subprocess
import socket

def test_port_listening(host, port, timeout=10):
    """测试端口是否在监听"""
    for i in range(timeout):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except Exception as e:
            pass
        time.sleep(1)
    return False

def main():
    print("=== Houdini服务器修复测试 ===")
    
    # 1. 启动服务器
    print("\n1. 启动服务器...")
    try:
        result = subprocess.run([
            sys.executable, "server_launcher.py", "--auto"
        ], capture_output=True, text=True, timeout=30)
        
        print(f"启动器返回码: {result.returncode}")
        print(f"输出: {result.stdout}")
        if result.stderr:
            print(f"错误: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("启动器超时，但这可能是正常的")
    except Exception as e:
        print(f"启动器错误: {e}")
    
    # 2. 测试端口监听
    print("\n2. 测试端口监听...")
    if test_port_listening("localhost", 18811):
        print("✓ 端口18811正在监听")
    else:
        print("✗ 端口18811未监听")
        return False
    
    # 3. 测试客户端连接
    print("\n3. 测试客户端连接...")
    try:
        # 简单的连接测试
        import hrpyc
        print("正在连接到服务器...")
        connection, hou = hrpyc.import_remote_module()
        print("✓ 客户端连接成功")
        
        # 测试基本功能
        service = hou.houdini_service
        info = service.get_server_info()
        print(f"✓ 服务器信息: {info}")
        
        connection.close()
        
    except Exception as e:
        print(f"✗ 客户端连接失败: {e}")
        return False
    
    print("\n=== 测试完成 ===")
    print("✓ 服务器修复成功！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 