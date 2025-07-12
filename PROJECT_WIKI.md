# Portable Houdini 项目 Wiki

## 项目概述

Portable Houdini 是一个便携的独立 Houdini 界面工具，能够在不需要打开 Houdini 的情况下加载 HDA 文件并调整参数，同时支持批处理配置。该工具采用 MVC 架构设计，使用 PySide2 构建 GUI 界面。

### 主要功能
- 独立加载和操作 HDA 文件
- 支持多种参数类型（字符串、数值、颜色、Ramp、按钮等）
- 批处理功能
- 3D 模型预览
- 多语言支持
- 主题切换
- 参数实时同步

## 技术栈

### 核心依赖
- **Python**: 3.7/3.9 (根据 Houdini 版本)
- **PySide2**: 5.15.2.1 - Qt 界面框架
- **PyOpenGL**: 3.1.7 - 3D 渲染
- **pyqtdarktheme**: 2.1.0 - 深色主题支持
- **darkdetect**: 0.7.1 - 系统主题检测
- **requests**: 2.28.0 - HTTP 请求

### 系统要求
- Windows 10/11
- 已安装并激活的 Houdini
- 对应版本的 Python 环境

## 项目架构

### 整体架构 (MVC 模式)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      View       │    │    Controller   │    │      Model      │
│   (GUI 界面)    │◄──►│   (业务逻辑)    │◄──►│   (数据模型)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 目录结构

```
PortableHoudini/
├── main.py                 # 程序入口点
├── requirements.txt        # 依赖包列表
├── icon.png               # 应用图标
├── README.md              # 项目说明
├── run_py37.bat          # Python 3.7 启动脚本
├── run_py39.bat          # Python 3.9 启动脚本
├── panel/                 # 主要代码目录
│   ├── main_panel.py      # 主窗口 (View)
│   ├── hda_panel.py       # HDA 参数面板 (View)
│   ├── hda_controller.py  # HDA 控制器 (Controller)
│   ├── hou_parms_model.py # Houdini 参数模型 (Model)
│   ├── batch_panel.py     # 批处理面板
│   ├── menu_*.py          # 菜单相关文件
│   ├── utils/             # 工具模块
│   │   ├── globals.py     # 全局变量
│   │   ├── settings_manager.py # 设置管理
│   │   ├── localization.py # 国际化
│   │   ├── theme.py       # 主题管理
│   │   ├── init_houdini.py # Houdini 初始化
│   │   └── ...
│   └── qwidget/           # 自定义 Qt 组件
│       ├── qt_mesh_viewer.py    # 3D 模型查看器
│       ├── qt_ramp.py           # Ramp 编辑器
│       ├── qt_color_selector.py # 颜色选择器
│       └── ...
├── test/                  # 测试文件
└── venv/                  # Python 虚拟环境
```

## 核心模块详解

### 1. 主程序入口 (main.py)

**功能**: 程序启动入口，负责初始化环境和启动主窗口

**关键特性**:
- 配置 Qt 插件路径
- 初始化全局变量
- 创建 MVC 组件
- 启动多线程 Houdini 控制器

**核心代码流程**:
```python
# 1. 环境配置
qt_plugin_path = os.path.join(os.path.dirname(sys.executable), r"Lib\site-packages\PySide2\plugins")
os.environ["QT_PLUGIN_PATH"] = qt_plugin_path

# 2. 创建 MVC 组件
model = HouParmsModel()
controller = HDAController(model)
window = MainWindow(model, controller)

# 3. 多线程启动
houdini_thread = QThread()
controller.moveToThread(houdini_thread)
houdini_thread.start()
```

### 2. 主窗口 (main_panel.py)

**功能**: 应用程序主窗口，管理整体界面布局

**组件结构**:
- 菜单栏 (文件、设置、窗口、帮助)
- HDA 参数面板
- 3D 模型预览面板
- 分割器布局

**关键方法**:
- `updateHDA()`: 更新 HDA 文件
- `saveHIP()`: 保存 HIP 文件
- `onOpenMeshViewer()`: 打开/关闭模型预览

### 3. HDA 控制器 (hda_controller.py)

**功能**: 业务逻辑控制器，处理 Houdini 节点操作

**核心特性**:
- 多线程队列处理
- HDA 文件加载和管理
- 参数值写入和同步
- 3D 模型更新

**关键组件**:
```python
class HDAController(QObject):
    cook_started = Signal()           # 开始计算信号
    cook_finished = Signal()          # 计算完成信号
    update_display_model = Signal()   # 模型更新信号
    
    # 队列处理机制
    def processQueue(self):
        while True:
            if self.queue.empty():
                time.sleep(0.5)
                continue
            process_type, parm_data = self.queue.get()
            # 处理参数更新
```

**参数处理流程**:
1. UI 触发参数变更
2. 信号发送到控制器
3. 参数加入处理队列
4. 工作线程处理队列
5. 写入 Houdini 节点
6. 触发模型更新

### 4. Houdini 参数模型 (hou_parms_model.py)

**功能**: 数据模型，管理 HDA 参数数据

**支持参数类型**:
- `STRING`: 字符串参数
- `FILE_STRING`: 文件路径参数
- `FLOAT/INT`: 数值参数
- `FLOAT_ARRAY/INT_ARRAY`: 数组参数
- `TOGGLE`: 开关参数
- `BUTTON`: 按钮参数
- `RAMP`: 渐变参数
- `COMBOX`: 下拉选择参数
- `COLOR`: 颜色参数

**数据流**:
```python
class HouParmsModel(QObject):
    view_datas_changed = Signal(list)      # 批量数据变更
    view_data_changed = Signal(HouParmMetadata)  # 单个数据变更
    controller_data_changed = Signal(HouParmMetadata)  # 控制器数据变更
```

### 5. 设置管理 (settings_manager.py)

**功能**: 应用程序设置管理，支持持久化存储

**设置项**:
- `HOUDINI_PATH`: Houdini 安装路径
- `LANGUAGE`: 界面语言
- `RECENT`: 最近打开的文件
- `THEME`: 主题设置

**存储位置**:
- Windows: `%APPDATA%\Portable Houdini\Settings.json`
- Linux/Mac: `~/.config/Portable Houdini/Settings.json`

### 6. 自定义 Qt 组件 (qwidget/)

**qt_mesh_viewer.py**: 3D 模型查看器
- 基于 OpenGL 的 3D 渲染
- 支持相机控制
- 实时模型更新

**qt_ramp.py**: Ramp 编辑器
- 可视化渐变编辑
- 支持多种插值方式
- 实时预览

**qt_color_selector.py**: 颜色选择器
- RGB/RGBA 颜色选择
- 颜色预览
- 数值输入

**qt_progress_bar.py**: 进度条
- 批处理进度显示
- 可取消操作

## 数据流和信号机制

### 参数更新流程

```
UI 组件 → Model.setParmFromView() → Signal → Controller.queueWriteHDAProperty()
                                    ↓
                             工作线程处理队列 → writeHDAProperty() → Houdini 节点
                                    ↓
                             模型更新 → updateNodeModel() → 3D 预览更新
```

### 信号连接

```python
# Model 到 Controller
model.view_data_changed.connect(controller.queueWriteHDAProperty)
model.view_datas_changed.connect(controller.queueWriteHDAProperties)

# Controller 到 UI
controller.cook_started.connect(progress_bar.show)
controller.cook_finished.connect(progress_bar.hide)
controller.update_display_model.connect(mesh_viewer.updateModel)
```

## 批处理功能

### 批处理机制
- 每个参数可设置多个批处理值
- 支持参数组合批处理
- 按钮类型支持批量触发
- 进度条显示处理进度

### 批处理流程
1. 用户设置批处理参数值
2. 系统计算总批次数
3. 按批次顺序执行参数设置
4. 每个批次完成后保存结果
5. 显示处理进度

## 国际化支持

### 支持语言
- 中文 (默认)
- English

### 实现方式
- 使用枚举管理语言字符串
- 动态语言切换
- 设置持久化存储

## 主题系统

### 主题类型
- `auto`: 跟随系统主题
- `light`: 浅色主题
- `dark`: 深色主题

### 实现
- 基于 pyqtdarktheme
- 支持系统主题检测
- 实时主题切换

## 开发指南

### 添加新参数类型
1. 在 `HouParamTypeEnum` 中添加新类型
2. 在 `hou_parms_model.py` 中添加类型判断逻辑
3. 在 `hda_controller.py` 中添加参数处理逻辑
4. 创建对应的 Qt 组件

### 添加新功能
1. 遵循 MVC 架构
2. 使用信号槽机制进行通信
3. 考虑多线程安全性
4. 添加国际化支持

### 调试技巧
- 使用 `print()` 输出调试信息
- 检查 Houdini 路径设置
- 验证 Python 版本兼容性
- 检查依赖包安装

## 部署说明

### 环境准备
1. 安装对应版本 Python
2. 安装 Houdini 并激活
3. 安装依赖包
4. 配置 Houdini 路径

### 打包发布
- 复制 Python 环境到 `venv/` 目录
- 创建启动脚本
- 测试功能完整性

## 已知问题和限制

### 当前限制
- 仅支持 Windows 平台
- 需要已安装的 Houdini
- 部分高级 HDA 功能可能不支持

### 待实现功能
- 保存/加载参数配置
- 文件夹和变量禁用/隐藏
- 表达式支持
- 客户端服务端分离

## 版本历史

### 当前版本特性
- ✅ 支持文件批处理
- ✅ 支持自动 Recook 开关
- ✅ 支持全部变量类型
- ✅ 支持 ToolTips
- ✅ 支持进度条显示
- ✅ 支持设置主题色
- ✅ 支持模型预览

### 计划功能
- 🔄 支持保存加载参数、批处理、hip
- 🔄 支持 folder、变量禁用和隐藏
- 🔄 支持简单属性窗口文件夹
- 🔄 支持前后端数据双向同步
- 🔄 客户端服务端分离 