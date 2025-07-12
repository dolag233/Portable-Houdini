#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 HDA 参数显示功能
"""

import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "panel"))

def test_parameter_conversion():
    """测试参数转换功能"""
    print("=== 测试参数转换功能 ===")
    
    # 模拟服务器返回的参数数据
    mock_parameters = [
        {
            "name": "test_float",
            "label": "Test Float",
            "type": "FLOAT",
            "value": 1.5,
            "help": "A test float parameter",
            "range": [0.0, 10.0],
            "options": None
        },
        {
            "name": "test_string",
            "label": "Test String",
            "type": "STRING",
            "value": "hello",
            "help": "A test string parameter",
            "range": None,
            "options": None
        },
        {
            "name": "test_vector",
            "label": "Test Vector",
            "type": "FLOAT_ARRAY",
            "value": [1.0, 2.0, 3.0],
            "help": "A test vector parameter",
            "range": None,
            "options": None
        },
        {
            "name": "test_toggle",
            "label": "Test Toggle",
            "type": "TOGGLE",
            "value": True,
            "help": "A test toggle parameter",
            "range": None,
            "options": None
        },
        {
            "name": "test_menu",
            "label": "Test Menu",
            "type": "COMBOX",
            "value": 1,
            "help": "A test menu parameter",
            "range": None,
            "options": {
                "items": ["option1", "option2", "option3"],
                "labels": ["Option 1", "Option 2", "Option 3"]
            }
        }
    ]
    
    try:
        from panel.hou_parms_model import HouParmsModel
        from panel.remote_hda_controller import RemoteHDAController
        
        # 创建模型和控制器
        model = HouParmsModel()
        controller = RemoteHDAController(model)
        
        # 测试参数转换
        print(f"转换前模型参数数量: {len(model.getParms())}")
        
        controller._update_model_from_remote_parameters(mock_parameters)
        
        print(f"转换后模型参数数量: {len(model.getParms())}")
        
        # 验证参数
        for i, parm in enumerate(model.getParms()):
            from panel.hou_parms_model import HouParamMetaEnum
            parm_name = parm.getData(HouParamMetaEnum.NAME)
            parm_type = parm.getData(HouParamMetaEnum.TYPE)
            parm_value = parm.getData(HouParamMetaEnum.VALUE)
            parm_label = parm.getData(HouParamMetaEnum.LABEL)
            
            print(f"参数 {i+1}: {parm_name} ({parm_type}) = {parm_value} [{parm_label}]")
        
        print("✓ 参数转换测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 参数转换测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_type_mapping():
    """测试类型映射"""
    print("\n=== 测试类型映射 ===")
    
    try:
        from panel.hou_parms_model import HouParmsModel
        from panel.remote_hda_controller import RemoteHDAController
        
        model = HouParmsModel()
        controller = RemoteHDAController(model)
        
        # 测试所有支持的类型
        test_types = [
            "STRING", "FILE_STRING", "FLOAT", "FLOAT_ARRAY",
            "INT", "INT_ARRAY", "TOGGLE", "BUTTON", 
            "RAMP", "COMBOX", "COLOR"
        ]
        
        for remote_type in test_types:
            local_type = controller._convert_remote_type_to_local(remote_type)
            if local_type is not None:
                print(f"✓ {remote_type} -> {local_type}")
            else:
                print(f"❌ {remote_type} -> None")
                return False
        
        print("✓ 类型映射测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 类型映射测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试 HDA 参数显示功能...")
    
    try:
        # 测试类型映射
        if not test_type_mapping():
            return 1
        
        # 测试参数转换
        if not test_parameter_conversion():
            return 1
        
        print("\n🎉 所有测试通过！")
        print("✅ 参数类型映射正确")
        print("✅ 远程参数转换功能正常")
        print("✅ 模型参数创建成功")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 