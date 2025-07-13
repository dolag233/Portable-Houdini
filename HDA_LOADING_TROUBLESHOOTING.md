# HDA加载问题故障排除指南

## 问题描述

在远程模式下加载HDA文件时，可能会遇到以下错误：
```
hou.OperationFailed: The attempted operation failed.
```

## 可能的原因

### 1. 文件传输问题
- **Base64编码损坏**：文件在网络传输过程中可能损坏
- **文件大小不匹配**：上传的文件大小与原始文件不一致
- **临时文件权限**：服务器端临时文件创建或访问权限问题

### 2. HDA文件兼容性
- **版本不兼容**：HDA文件可能是用不同版本的Houdini创建的
- **文件格式问题**：HDA文件本身可能损坏或格式不正确
- **路径编码问题**：Windows路径分隔符或编码问题

### 3. Houdini环境问题
- **许可证问题**：服务器端Houdini许可证可能有问题
- **环境变量**：Houdini环境变量设置不正确
- **Python环境**：Python路径或模块加载问题

## 解决方案

### 方案1: 检查文件传输完整性

1. **查看上传日志**：
   ```
   正在上传文件: BoxGeneratorTest.hda (17936 bytes)
   Base64编码: 17936 bytes -> 23915 chars
   ✅ 文件上传成功: BoxGeneratorTest.hda (大小验证通过)
   ```

2. **如果大小不匹配**：
   - 重新启动服务器和客户端
   - 检查网络连接稳定性
   - 尝试使用较小的HDA文件测试

### 方案2: 验证HDA文件有效性

1. **在本地Houdini中测试**：
   - 直接在Houdini中打开HDA文件
   - 确认文件可以正常加载和使用

2. **检查HDA文件信息**：
   ```python
   # 在Houdini的Python Shell中运行
   import hou
   definitions = hou.hda.definitionsInFile("path/to/your.hda")
   print(f"找到 {len(definitions)} 个定义")
   for def in definitions:
       print(f"类型: {def.nodeTypeName()}")
       print(f"版本: {def.version()}")
   ```

### 方案3: 使用不同的HDA文件测试

1. **创建简单的测试HDA**：
   - 在Houdini中创建一个简单的几何节点
   - 保存为HDA文件
   - 尝试加载这个简单的HDA

2. **使用项目中的其他HDA**：
   - 尝试加载 `test/TestHDA.hda`
   - 比较不同HDA文件的加载结果

### 方案4: 服务器端诊断

1. **检查服务器日志**：
   ```
   === 开始加载HDA ===
   原始HDA路径: C:\Users\...\temp\BoxGeneratorTest.hda
   规范化路径: C:/Users/.../temp/BoxGeneratorTest.hda
   文件大小: 17936 bytes
   ✅ HDA文件头部验证通过
   ```

2. **查看详细错误信息**：
   - 服务器会打印完整的错误堆栈
   - 查看具体在哪一步失败

### 方案5: 环境配置检查

1. **确认Houdini版本**：
   - 客户端和服务器使用相同版本的Houdini
   - 检查HDA文件创建时使用的Houdini版本

2. **检查许可证**：
   - 确保服务器端Houdini许可证有效
   - 验证可以正常启动Houdini

## 临时解决方案

### 方案A: 手动复制文件

如果文件传输有问题，可以手动将HDA文件复制到服务器：

1. **找到服务器临时目录**：
   ```
   临时文件目录: C:\Users\...\AppData\Local\Temp\houdini_server_xxxxx
   ```

2. **手动复制HDA文件**：
   - 将HDA文件复制到服务器的临时目录
   - 使用相同的文件名

3. **修改客户端代码**：
   - 跳过文件上传步骤
   - 直接使用服务器端的文件路径

### 方案B: 使用共享目录

1. **设置网络共享目录**：
   - 客户端和服务器都能访问的共享文件夹
   - 将HDA文件放在共享目录中

2. **修改加载逻辑**：
   - 客户端提供共享路径
   - 服务器直接从共享路径加载

## 调试步骤

### 步骤1: 基本验证
```bash
# 1. 检查文件是否存在
ls -la test/BoxGeneratorTest.hda

# 2. 检查文件大小
stat test/BoxGeneratorTest.hda
```

### 步骤2: 服务器端测试
```python
# 在服务器端Houdini环境中运行
import hou
import os

# 测试文件路径
hda_path = "C:/path/to/your.hda"

# 检查文件
print(f"文件存在: {os.path.exists(hda_path)}")
print(f"文件大小: {os.path.getsize(hda_path)}")

# 尝试加载
try:
    definitions = hou.hda.definitionsInFile(hda_path)
    print(f"成功: 找到 {len(definitions)} 个定义")
except Exception as e:
    print(f"失败: {e}")
```

### 步骤3: 网络传输测试
```python
# 测试Base64编码/解码
import base64

# 读取文件
with open("test/BoxGeneratorTest.hda", "rb") as f:
    original = f.read()

# 编码解码
encoded = base64.b64encode(original).decode('utf-8')
decoded = base64.b64decode(encoded)

# 验证
print(f"原始大小: {len(original)}")
print(f"解码大小: {len(decoded)}")
print(f"内容一致: {original == decoded}")
```

## 联系支持

如果以上方案都无法解决问题，请提供以下信息：

1. **完整的错误日志**（客户端和服务器端）
2. **Houdini版本信息**
3. **操作系统信息**
4. **HDA文件信息**（大小、创建版本等）
5. **网络环境**（本地/远程）

## 已知问题

### 问题1: Windows路径分隔符
- **现象**：路径包含反斜杠导致加载失败
- **解决**：系统会自动尝试多种路径格式

### 问题2: 文件编码问题
- **现象**：Base64编码后文件损坏
- **解决**：增加了文件完整性验证

### 问题3: Houdini版本兼容性
- **现象**：不同版本创建的HDA无法加载
- **解决**：使用相同版本的Houdini创建和加载HDA 