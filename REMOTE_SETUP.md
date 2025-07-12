# Portable Houdini 远程模式设置指南

## 概述

Portable Houdini 现在支持客户端-服务器分离模式，可以在以下场景中使用：

1. **本地模式**：直接在本地运行 Houdini（原有模式）
2. **远程模式**：连接到远程 Houdini 服务器

## 架构说明

```
┌─────────────────┐    hrpyc    ┌─────────────────┐
│   客户端 (GUI)   │ ◄────────► │ 服务器 (Houdini) │
│  - 用户界面      │   TCP/IP   │  - HDA 处理     │
│  - 参数控制      │            │  - 几何计算     │
│  - 批处理管理    │            │  - 模型预览     │
│  - 文件传输      │            │  - 临时文件管理 │
└─────────────────┘            └─────────────────┘
```

## 文件传输功能

### 自动文件传输
- 当您在客户端打开本地HDA文件时，系统会自动将文件传输到服务器
- 文件使用Base64编码进行安全传输
- 服务器端创建临时文件进行处理
- 支持任意大小的HDA文件传输

### 临时文件管理
- 服务器端自动创建临时目录存储上传的文件
- 应用关闭时自动清理临时文件
- 切换HDA时自动清理之前的临时文件
- 防止服务器端文件积累

## 快速开始

### 1. 启动服务器

#### 自动模式（推荐）
双击 `start_server.bat` 或在命令行运行：
```bash
python server_launcher.py --auto
```

#### 手动模式
```bash
# 列出所有检测到的 Houdini 安装
python server_launcher.py --list

# 手动指定 Houdini 路径
python server_launcher.py --houdini-path "C:\Program Files\Side Effects Software\Houdini 19.5.493"

# 指定服务器地址和端口
python server_launcher.py --host 0.0.0.0 --port 18811
```

### 2. 配置客户端

1. 启动 Portable Houdini 客户端
2. 点击菜单 `设置` → `服务器连接设置`
3. 选择工作模式：
   - **本地模式**：直接使用本地 Houdini
   - **远程模式**：连接到远程服务器
4. 如果选择远程模式，配置服务器连接信息
5. 点击"连接"按钮

### 3. 使用远程HDA

1. **连接到服务器**：确保状态栏显示"🟢 已连接"
2. **打开本地HDA**：通过"文件" → "打开HDA文件"选择本地HDA文件
3. **自动传输**：系统会自动将文件传输到服务器并加载
4. **正常使用**：像使用本地HDA一样调整参数和预览模型

## 详细配置

### 服务器端配置

服务器设置保存在 `server_settings.json` 文件中：

```json
{
  "houdini_path": "C:\\Program Files\\Side Effects Software\\Houdini 19.5.493",
  "python_path": "C:\\Program Files\\Side Effects Software\\Houdini 19.5.493\\bin\\python.exe",
  "server_port": 18811,
  "server_host": "localhost",
  "auto_start": false,
  "selected_installation": {
    "name": "Houdini 19.5.493",
    "path": "C:\\Program Files\\Side Effects Software\\Houdini 19.5.493",
    "python_path": "C:\\Program Files\\Side Effects Software\\Houdini 19.5.493\\bin\\python.exe",
    "version": "19.5"
  }
}
```

### 客户端配置

客户端设置保存在 `client_settings.json` 文件中：

```json
{
  "server_host": "localhost",
  "server_port": 18811,
  "connection_timeout": 10,
  "retry_interval": 5,
  "max_retries": 3,
  "auto_reconnect": true
}
```

## 网络配置

### 本地使用
- 服务器地址：`localhost` 或 `127.0.0.1`
- 端口：`18811`（默认）

### 远程使用
- 确保服务器端口（默认 18811）在防火墙中开放
- 服务器地址设置为 `0.0.0.0` 以监听所有网络接口
- 客户端使用服务器的实际 IP 地址

### 防火墙设置

#### Windows 防火墙
```cmd
# 允许入站连接（在服务器端执行）
netsh advfirewall firewall add rule name="Houdini RPC Server" dir=in action=allow protocol=TCP localport=18811
```

#### Linux 防火墙 (ufw)
```bash
# 允许端口访问
sudo ufw allow 18811/tcp
```

## 使用方法

### 基本操作

1. **加载 HDA**：在客户端选择本地HDA文件，系统自动传输并在服务器加载
2. **参数调整**：所有参数修改会实时同步到服务器
3. **批处理**：批处理操作在服务器端执行
4. **模型预览**：几何数据从服务器传输到客户端显示

### 文件传输详情

1. **支持的文件类型**：
   - `.hda` - Houdini Digital Asset
   - `.vtl` - Houdini VTL文件
   - 其他Houdini支持的资产文件

2. **传输过程**：
   - 客户端读取本地文件
   - 使用Base64编码进行网络传输
   - 服务器端解码并创建临时文件
   - 使用临时文件路径加载HDA

3. **性能考虑**：
   - 大文件传输可能需要几秒钟时间
   - 网络带宽影响传输速度
   - 建议在稳定网络环境下使用

### 性能优化

1. **网络延迟**：
   - 本地网络：< 1ms 延迟
   - 广域网：建议 < 100ms 延迟

2. **数据传输**：
   - 参数数据：很小，实时传输
   - HDA文件：中等大小，按需传输
   - 几何数据：较大，按需传输

3. **文件大小建议**：
   - 小文件（< 1MB）：传输快速
   - 中等文件（1-10MB）：传输稍慢但可接受
   - 大文件（> 10MB）：建议使用高速网络

## 故障排除

### 常见问题

1. **文件传输失败**：
   - 检查网络连接
   - 确认服务器有足够磁盘空间
   - 检查文件权限

2. **HDA加载失败**：
   - 确认文件格式正确
   - 检查Houdini版本兼容性
   - 查看服务器端错误日志

3. **临时文件问题**：
   - 服务器会自动清理临时文件
   - 手动清理：重启服务器或客户端
   - 检查临时目录权限

### 调试信息

启动时会显示：
```
临时文件目录: C:\Users\...\AppData\Local\Temp\houdini_server_xxxxx
文件上传成功: BoxGeneratorTest.hda -> C:\Users\...\Temp\houdini_server_xxxxx\BoxGeneratorTest.hda
```

## 安全考虑

1. **网络安全**：
   - 仅在可信网络环境中使用
   - 考虑使用VPN进行远程访问
   - 定期更新防火墙规则

2. **文件安全**：
   - 临时文件自动清理
   - 不在服务器端永久存储客户端文件
   - 使用安全的编码传输

3. **访问控制**：
   - 默认只监听localhost
   - 远程访问需要明确配置
   - 建议使用强密码保护服务器主机 