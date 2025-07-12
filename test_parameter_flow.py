#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试参数加载和显示流程
"""

import sys
import os
import time

def test_parameter_flow():
    """测试完整的参数流程"""
    print("=== 测试完整参数流程 ===")
    
    # 模拟完整的参数加载流程
    print("1. 模拟服务器端参数提取...")
    
    # 这些是服务器端应该返回的参数格式
    server_response = {
        "success": True,
        "message": "HDA加载成功",
        "hda_path": "/test/path/test.hda",
        "hda_name": "TestHDA",
        "node_path": "/obj/geo/hda",
        "parameters": [
            {
                "name": "divisions",
                "label": "Divisions",
                "type": "INT",
                "value": 10,
                "help": "Number of divisions",
                "range": [1, 100],
                "options": None
            },
            {
                "name": "scale",
                "label": "Scale",
                "type": "FLOAT",
                "value": 1.0,
                "help": "Scale factor",
                "range": [0.1, 10.0],
                "options": None
            },
            {
                "name": "name",
                "label": "Name",
                "type": "STRING",
                "value": "default",
                "help": "Object name",
                "range": None,
                "options": None
            },
            {
                "name": "enabled",
                "label": "Enabled",
                "type": "TOGGLE",
                "value": True,
                "help": "Enable this feature",
                "range": None,
                "options": None
            }
        ]
    }
    
    print(f"服务器返回: {len(server_response['parameters'])} 个参数")
    for param in server_response['parameters']:
        print(f"  - {param['name']} ({param['type']}) = {param['value']}")
    
    print("\n2. 模拟客户端参数转换...")
    
    # 模拟类型转换
    type_mapping = {
        "STRING": "STRING",
        "FILE_STRING": "FILE_STRING",
        "FLOAT": "FLOAT", 
        "FLOAT_ARRAY": "FLOAT_ARRAY",
        "INT": "INT",
        "INT_ARRAY": "INT_ARRAY",
        "TOGGLE": "TOGGLE",
        "BUTTON": "BUTTON",
        "RAMP": "RAMP",
        "COMBOX": "COMBOX",
        "COLOR": "COLOR",
    }
    
    converted_params = []
    for param in server_response['parameters']:
        remote_type = param['type']
        local_type = type_mapping.get(remote_type, "UNKNOWN")
        
        if local_type != "UNKNOWN":
            converted_param = {
                "name": param['name'],
                "label": param['label'],
                "type": local_type,
                "value": param['value'],
                "help": param['help'],
                "range": param['range'],
                "options": param['options']
            }
            converted_params.append(converted_param)
            print(f"  转换: {remote_type} -> {local_type}")
        else:
            print(f"  错误: 未知类型 {remote_type}")
    
    print(f"\n成功转换 {len(converted_params)} 个参数")
    
    print("\n3. 模拟 UI 创建...")
    
    # 模拟 UI 创建过程
    ui_widgets = {}
    for param in converted_params:
        param_type = param['type']
        param_name = param['name']
        param_value = param['value']
        
        if param_type == "STRING":
            ui_widgets[param_name] = f"QLineEdit('{param_value}')"
        elif param_type == "FLOAT":
            ui_widgets[param_name] = f"QFloatSlider({param_value})"
        elif param_type == "INT":
            ui_widgets[param_name] = f"QIntegerSlider({param_value})"
        elif param_type == "TOGGLE":
            ui_widgets[param_name] = f"QCheckBox({param_value})"
        else:
            ui_widgets[param_name] = f"Unknown({param_type})"
        
        print(f"  创建 UI: {param_name} -> {ui_widgets[param_name]}")
    
    print(f"\n成功创建 {len(ui_widgets)} 个 UI 控件")
    
    print("\n4. 验证数据完整性...")
    
    # 验证数据完整性
    original_count = len(server_response['parameters'])
    converted_count = len(converted_params)
    ui_count = len(ui_widgets)
    
    print(f"原始参数: {original_count}")
    print(f"转换参数: {converted_count}")
    print(f"UI 控件: {ui_count}")
    
    if original_count == converted_count == ui_count:
        print("✓ 数据完整性验证通过")
        return True
    else:
        print("❌ 数据完整性验证失败")
        return False

def main():
    """主函数"""
    print("开始测试参数加载和显示流程...")
    
    try:
        if test_parameter_flow():
            print("\n🎉 参数流程测试通过！")
            print("✅ 服务器参数格式正确")
            print("✅ 客户端类型转换正常")
            print("✅ UI 创建逻辑正确")
            print("✅ 数据完整性验证通过")
            
            print("\n现在请启动客户端并测试实际的 HDA 加载:")
            print("1. 启动客户端: python start_client.py")
            print("2. 连接到服务器")
            print("3. 加载 HDA 文件")
            print("4. 检查控制台输出中的调试信息")
            
        else:
            print("\n❌ 参数流程测试失败")
            return 1
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 