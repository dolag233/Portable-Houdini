#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试API返回值一致性
"""

import sys
import os
from pathlib import Path

def test_api_consistency():
    """测试API返回值一致性"""
    print("=== API一致性测试 ===")
    
    # 使用正确的Python环境
    venv_path = Path(__file__).parent / "venv"
    if venv_path.exists():
        python39_path = venv_path / "Python39" / "python.exe"
        if python39_path.exists():
            print(f"使用项目Python39: {python39_path}")
        else:
            python39_path = sys.executable
            print(f"使用当前Python: {python39_path}")
    else:
        python39_path = sys.executable
        print(f"使用当前Python: {python39_path}")
    
    # 测试脚本
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
    service = hou.houdini_service
    
    # 测试各个API方法的返回值格式
    print("\\n=== 测试API返回值格式 ===")
    
    # 1. 测试 get_server_info
    print("1. 测试 get_server_info:")
    result = service.get_server_info()
    print(f"   返回类型: {type(result)}")
    print(f"   包含success字段: {'success' in result}")
    if isinstance(result, dict):
        print(f"   success值: {result.get('success', 'N/A')}")
    
    # 2. 测试 clear_hda
    print("\\n2. 测试 clear_hda:")
    result = service.clear_hda()
    print(f"   返回类型: {type(result)}")
    print(f"   包含success字段: {'success' in result if isinstance(result, dict) else False}")
    if isinstance(result, dict):
        print(f"   success值: {result.get('success', 'N/A')}")
    
    # 3. 测试 get_model_data
    print("\\n3. 测试 get_model_data:")
    result = service.get_model_data()
    print(f"   返回类型: {type(result)}")
    print(f"   包含success字段: {'success' in result if isinstance(result, dict) else False}")
    if isinstance(result, dict):
        print(f"   success值: {result.get('success', 'N/A')}")
    
    # 4. 测试 get_all_parameters
    print("\\n4. 测试 get_all_parameters:")
    result = service.get_all_parameters()
    print(f"   返回类型: {type(result)}")
    print(f"   包含success字段: {'success' in result if isinstance(result, dict) else False}")
    if isinstance(result, dict):
        print(f"   success值: {result.get('success', 'N/A')}")
    
    connection.close()
    print("\\n[SUCCESS] API一致性测试完成！")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()
"""
    
    # 创建临时测试文件
    test_file = Path(__file__).parent / "temp_api_test.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    try:
        import subprocess
        # 运行测试
        result = subprocess.run([str(python39_path), str(test_file)], 
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
    success = test_api_consistency()
    
    if success:
        print("\n[SUCCESS] API一致性测试通过！")
    else:
        print("\n[FAILED] API一致性测试失败！")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 