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
└─────────────────┘            └─────────────────┘
```

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

1. **加载 HDA**：在客户端选择 HDA 文件，服务器会自动加载
2. **参数调整**：所有参数修改会实时同步到服务器
3. **批处理**：批处理操作在服务器端执行
4. **模型预览**：几何数据从服务器传输到客户端显示

### 性能优化

1. **网络延迟**：
   - 本地网络：< 1ms 延迟
   - 广域网：建议 < 100ms 延迟

2. **数据传输**：
   - 参数数据：很小，实时传输
   - 几何数据：较大，按需传输

3. **服务器资源**：
   - CPU：Houdini 计算需求
   - 内存：根据 HDA 复杂度
   - 存储：临时文件和缓存

## 故障排除

### 常见问题

#### 1. 服务器无法启动
```
错误：无法导入 Houdini 模块
```
**解决方案**：
- 确保使用 Houdini 的 Python 环境
- 检查 Houdini 安装路径
- 验证 Houdini 许可证

#### 2. 客户端连接失败
```
错误：连接失败: [Errno 10061] 由于目标计算机积极拒绝，无法连接
```
**解决方案**：
- 检查服务器是否正在运行
- 验证 IP 地址和端口
- 检查防火墙设置

#### 3. 参数同步问题
```
错误：设置参数失败
```
**解决方案**：
- 检查网络连接稳定性
- 重新加载 HDA
- 重启服务器

### 调试模式

启用调试模式获取更多信息：

```bash
# 服务器调试模式
python houdini_server.py --debug

# 客户端调试模式
# 在连接对话框中查看连接日志
```

### 日志文件

- 服务器日志：控制台输出
- 客户端日志：连接对话框中的日志窗口

## 安全注意事项

1. **网络安全**：
   - hrpyc 不提供身份验证
   - 仅在可信网络中使用
   - 考虑使用 VPN 或防火墙限制访问

2. **文件访问**：
   - 服务器可以访问本地文件系统
   - 确保 HDA 文件路径安全

3. **资源限制**：
   - 服务器没有资源限制
   - 复杂的 HDA 可能消耗大量资源

## 部署建议

### 开发环境
- 本地模式：快速开发和测试
- 远程模式：团队协作

### 生产环境
- 专用服务器：高性能计算
- 负载均衡：多个服务器实例
- 监控：服务器状态和性能

### 云部署
- AWS/Azure/GCP：按需计算资源
- 容器化：Docker 部署
- 自动扩缩：根据负载调整

## 技术细节

### 通信协议
- **传输层**：TCP/IP
- **应用层**：hrpyc (基于 rpyc)
- **数据格式**：Python 对象序列化

### 支持的操作
- HDA 加载和卸载
- 参数设置（单个和批量）
- 几何数据获取
- HIP 文件保存
- 服务器状态查询

### 限制
- 不支持实时交互（如视口操作）
- 大型几何数据传输可能较慢
- 网络中断会导致连接丢失

## 更新说明

### 版本兼容性
- 客户端和服务器应使用相同版本
- Houdini 版本兼容性取决于 HDA

### 升级步骤
1. 停止服务器
2. 更新代码
3. 重启服务器
4. 更新客户端

## 支持和反馈

如果遇到问题或有改进建议，请：

1. 检查本文档的故障排除部分
2. 查看控制台和日志输出
3. 记录详细的错误信息和重现步骤
4. 提供系统环境信息（操作系统、Houdini 版本等） 