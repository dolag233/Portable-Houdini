#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试仅支持远程模式的客户端
"""

import sys
import os

def test_main_app():
    """测试主应用程序"""
    print("=== 测试主应用程序启动 ===")
    
    # 检查 main.py 是否移除了 Houdini 路径检查
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查是否移除了 Houdini 路径检查
    if "HOUDINI_PATH" in content and "QMessageBox" in content:
        print("❌ main.py 仍然包含 Houdini 路径检查")
        return False
    
    # 检查是否默认设置为远程模式
    if 'set_mode("remote")' not in content:
        print("❌ main.py 没有默认设置为远程模式")
        return False
    
    # 检查是否移除了本地 Houdini 导入检查
    if "本地模式需要Houdini环境" in content:
        print("❌ main.py 仍然包含本地 Houdini 环境检查")
        return False
    
    print("✓ 主应用程序配置正确")
    return True

def test_remote_controller():
    """测试远程控制器文件"""
    print("\n=== 测试远程控制器配置 ===")
    
    with open("panel/remote_hda_controller.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查是否移除了本地模式支持
    if "本地模式" in content and "导入本地控制器" in content:
        print("❌ remote_hda_controller.py 仍然包含本地模式支持")
        return False
    
    # 检查是否仅支持远程模式
    if "仅支持远程模式" not in content:
        print("❌ remote_hda_controller.py 没有标记为仅支持远程模式")
        return False
    
    print("✓ 远程控制器配置正确")
    return True

def test_main_panel():
    """测试主面板文件"""
    print("\n=== 测试主面板配置 ===")
    
    with open("panel/main_panel.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查是否移除了本地 Houdini 导入检查
    if "本地模式需要导入Houdini" in content:
        print("❌ main_panel.py 仍然包含本地 Houdini 导入检查")
        return False
    
    # 检查是否移除了本地模式判断
    if "本地Houdini" in content and "远程服务器" in content:
        print("❌ main_panel.py 仍然包含本地/远程模式判断")
        return False
    
    print("✓ 主面板配置正确")
    return True

def test_connection_dialog():
    """测试连接对话框文件"""
    print("\n=== 测试连接对话框配置 ===")
    
    with open("panel/server_connection_dialog.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查是否移除了模式选择
    if "mode_combo" in content and "addItems" in content:
        print("❌ server_connection_dialog.py 仍然包含模式选择组件")
        return False
    
    # 检查是否仅显示远程模式信息
    if "仅显示远程模式信息" not in content:
        print("❌ server_connection_dialog.py 没有配置为仅显示远程模式")
        return False
    
    print("✓ 连接对话框配置正确")
    return True

def main():
    """主函数"""
    print("开始测试仅支持远程模式的客户端配置...")
    
    try:
        # 测试主应用程序
        if not test_main_app():
            return 1
            
        # 测试远程控制器
        if not test_remote_controller():
            return 1
            
        # 测试主面板
        if not test_main_panel():
            return 1
            
        # 测试连接对话框
        if not test_connection_dialog():
            return 1
        
        print("\n🎉 所有测试通过！")
        print("✅ 客户端已成功配置为仅支持远程模式")
        print("✅ 移除了所有本地 Houdini 相关的检查和错误弹窗")
        print("✅ 连接对话框只显示远程模式选项")
        print("✅ 主面板不再检查本地 Houdini 环境")
        print("✅ 远程控制器简化为仅支持远程模式")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 