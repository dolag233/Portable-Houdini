#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Houdini Server Launcher
自动检测Houdini安装路径并启动服务器
"""

import os
import sys
import platform
import subprocess
import json
import argparse
import time
from pathlib import Path

# Windows注册表检测
if platform.system() == "Windows":
    try:
        import winreg
    except ImportError:
        import _winreg as winreg


class HoudiniDetector:
    """Houdini安装路径检测器"""
    
    def __init__(self):
        self.system = platform.system()
        self.detected_installations = []
    
    def detect_houdini_installations(self):
        """检测所有Houdini安装"""
        if self.system == "Windows":
            return self._detect_windows_installations()
        elif self.system == "Darwin":  # macOS
            return self._detect_macos_installations()
        else:  # Linux
            return self._detect_linux_installations()
    
    def _detect_windows_installations(self):
        """检测Windows下的Houdini安装"""
        installations = []
        
        # 检查注册表
        try:
            # 检查HKEY_LOCAL_MACHINE\SOFTWARE\Side Effects Software
            key_path = r"SOFTWARE\Side Effects Software"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("Houdini"):
                            subkey_path = key_path + "\\" + subkey_name
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey_path) as subkey:
                                try:
                                    install_path, _ = winreg.QueryValueEx(subkey, "InstallPath")
                                    if os.path.exists(install_path):
                                        python_path = self._find_houdini_python(install_path)
                                        if python_path:
                                            installations.append({
                                                "name": subkey_name,
                                                "path": install_path,
                                                "python_path": python_path,
                                                "version": self._extract_version(subkey_name)
                                            })
                                except FileNotFoundError:
                                    pass
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            print(f"注册表检测失败: {e}")
        
        # 检查常见安装目录
        common_paths = [
            r"C:\Program Files\Side Effects Software",
            r"C:\Program Files (x86)\Side Effects Software"
        ]
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    if item.startswith("Houdini"):
                        install_path = os.path.join(base_path, item)
                        if os.path.isdir(install_path):
                            python_path = self._find_houdini_python(install_path)
                            if python_path and not any(inst["path"] == install_path for inst in installations):
                                installations.append({
                                    "name": item,
                                    "path": install_path,
                                    "python_path": python_path,
                                    "version": self._extract_version(item)
                                })
        
        return installations
    
    def _detect_macos_installations(self):
        """检测macOS下的Houdini安装"""
        installations = []
        
        # 检查/Applications目录
        apps_dir = "/Applications"
        if os.path.exists(apps_dir):
            for item in os.listdir(apps_dir):
                if item.startswith("Houdini") and item.endswith(".app"):
                    app_path = os.path.join(apps_dir, item)
                    if os.path.isdir(app_path):
                        # macOS应用包结构
                        framework_path = os.path.join(app_path, "Contents", "Frameworks", "Houdini.framework", "Versions", "Current", "Resources")
                        if os.path.exists(framework_path):
                            python_path = self._find_houdini_python(framework_path)
                            if python_path:
                                installations.append({
                                    "name": item.replace(".app", ""),
                                    "path": framework_path,
                                    "python_path": python_path,
                                    "version": self._extract_version(item)
                                })
        
        return installations
    
    def _detect_linux_installations(self):
        """检测Linux下的Houdini安装"""
        installations = []
        
        # 检查常见安装目录
        common_paths = [
            "/opt/hfs*",
            "/usr/local/hfs*",
            os.path.expanduser("~/houdini_installations/hfs*")
        ]
        
        import glob
        for pattern in common_paths:
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    python_path = self._find_houdini_python(path)
                    if python_path:
                        installations.append({
                            "name": os.path.basename(path),
                            "path": path,
                            "python_path": python_path,
                            "version": self._extract_version(os.path.basename(path))
                        })
        
        return installations
    
    def _find_houdini_python(self, houdini_path):
        """查找Houdini的Python可执行文件"""
        if self.system == "Windows":
            # 首先检查bin目录下的python.exe
            bin_python = os.path.join(houdini_path, "bin", "python.exe")
            if os.path.exists(bin_python):
                return bin_python
            
            # 然后检查所有python版本目录
            python_dirs = []
            if os.path.exists(houdini_path):
                for item in os.listdir(houdini_path):
                    if item.startswith("python") and os.path.isdir(os.path.join(houdini_path, item)):
                        python_exe = os.path.join(houdini_path, item, "python.exe")
                        if os.path.exists(python_exe):
                            python_dirs.append((item, python_exe))
            
            # 按版本号排序，优先使用更高版本
            python_dirs.sort(key=lambda x: self._extract_python_version(x[0]), reverse=True)
            
            if python_dirs:
                return python_dirs[0][1]
        else:
            # Linux/macOS
            python_paths = [
                os.path.join(houdini_path, "bin", "python"),
                os.path.join(houdini_path, "python", "bin", "python")
            ]
            
            for python_path in python_paths:
                if os.path.exists(python_path):
                    return python_path
            
            # 检查python版本目录
            if os.path.exists(houdini_path):
                for item in os.listdir(houdini_path):
                    if item.startswith("python") and os.path.isdir(os.path.join(houdini_path, item)):
                        python_exe = os.path.join(houdini_path, item, "bin", "python")
                        if os.path.exists(python_exe):
                            return python_exe
        
        return None
    
    def _extract_version(self, name):
        """从名称中提取版本号"""
        import re
        match = re.search(r'(\d+\.\d+)', name)
        return match.group(1) if match else "Unknown"
    
    def _extract_python_version(self, python_dir_name):
        """从Python目录名称中提取版本号用于排序"""
        import re
        # 提取版本号，如 python37 -> 37, python39 -> 39, python310 -> 310
        match = re.search(r'python(\d+)', python_dir_name.lower())
        if match:
            version_str = match.group(1)
            if len(version_str) == 2:  # 如 37, 39
                return int(version_str)
            elif len(version_str) == 3:  # 如 310, 311
                return int(version_str)
            else:
                return 0
        return 0


class HoudiniServerLauncher:
    """Houdini服务器启动器"""
    
    def __init__(self):
        self.detector = HoudiniDetector()
        self.settings_file = "server_settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self):
        """加载服务器设置"""
        default_settings = {
            "houdini_path": "",
            "python_path": "",
            "server_port": 18811,
            "server_host": "localhost",
            "auto_start": False,
            "selected_installation": None
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 合并默认设置
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception as e:
                print(f"加载设置失败: {e}")
        
        return default_settings
    
    def save_settings(self):
        """保存服务器设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def select_houdini_installation(self, installations=None):
        """选择Houdini安装"""
        if installations is None:
            installations = self.detector.detect_houdini_installations()
        
        if not installations:
            print("未找到Houdini安装，请手动指定路径")
            return None
        
        print("检测到以下Houdini安装:")
        for i, inst in enumerate(installations):
            print(f"{i + 1}. {inst['name']} (版本: {inst['version']})")
            print(f"   路径: {inst['path']}")
            print(f"   Python: {inst['python_path']}")
            print()
        
        while True:
            try:
                choice = input(f"请选择要使用的Houdini安装 (1-{len(installations)}): ")
                index = int(choice) - 1
                if 0 <= index < len(installations):
                    selected = installations[index]
                    self.settings["houdini_path"] = selected["path"]
                    self.settings["python_path"] = selected["python_path"]
                    self.settings["selected_installation"] = selected
                    self.save_settings()
                    return selected
                else:
                    print("无效选择，请重试")
            except ValueError:
                print("请输入有效数字")
            except KeyboardInterrupt:
                print("\n用户取消")
                return None
    
    def start_server(self, installation=None):
        """启动Houdini服务器"""
        if installation is None:
            if self.settings.get("selected_installation"):
                installation = self.settings["selected_installation"]
            else:
                installations = self.detector.detect_houdini_installations()
                installation = self.select_houdini_installation(installations)
        
        if not installation:
            print("无法启动服务器：未选择Houdini安装")
            return False
        
        print(f"正在启动Houdini服务器...")
        print(f"使用安装: {installation['name']}")
        print(f"Python路径: {installation['python_path']}")
        print(f"服务器地址: {self.settings['server_host']}:{self.settings['server_port']}")
        
        # 设置环境变量
        env = os.environ.copy()
        env["HFS"] = installation["path"]
        
        # 构建启动命令
        server_script = os.path.join(os.path.dirname(__file__), "houdini_server.py")
        cmd = [
            installation["python_path"],
            server_script,
            "--host", self.settings["server_host"],
            "--port", str(self.settings["server_port"])
        ]
        
        try:
            # 启动服务器进程
            print("启动命令:", " ".join(cmd))
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 合并stderr到stdout
                text=True,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            
            # 等待一段时间检查进程是否正常启动
            startup_timeout = 10  # 10秒超时
            output_lines = []
            
            for i in range(startup_timeout):
                time.sleep(1)
                
                # 检查进程是否还在运行
                if process.poll() is not None:
                    # 进程已退出，读取输出
                    stdout, stderr = process.communicate()
                    print(f"服务器启动失败，进程已退出 (返回码: {process.returncode})")
                    print("输出:")
                    print(stdout)
                    return False
                
                # 尝试读取输出
                try:
                    line = process.stdout.readline()
                    if line:
                        output_lines.append(line.strip())
                        print(f"服务器输出: {line.strip()}")
                        
                        # 检查是否有成功启动的标志
                        if "服务器启动成功" in line:
                            print("服务器启动成功！")
                            print(f"PID: {process.pid}")
                            return True
                            
                        # 检查是否有错误信息
                        if "失败" in line or "错误" in line or "Error" in line:
                            print(f"检测到错误: {line.strip()}")
                            
                except Exception as e:
                    print(f"读取输出时出错: {e}")
                    
            # 超时了，但进程仍在运行
            if process.poll() is None:
                print("服务器启动超时，但进程仍在运行")
                print(f"PID: {process.pid}")
                print("请检查服务器是否正常启动")
                return True
            else:
                print("服务器启动失败：进程意外退出")
                return False
                
        except Exception as e:
            print(f"启动服务器时发生错误: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Houdini服务器启动器")
    parser.add_argument("--auto", action="store_true", help="自动启动模式")
    parser.add_argument("--host", default="localhost", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=18811, help="服务器端口")
    parser.add_argument("--houdini-path", help="手动指定Houdini安装路径")
    parser.add_argument("--list", action="store_true", help="列出所有检测到的Houdini安装")
    
    args = parser.parse_args()
    
    launcher = HoudiniServerLauncher()
    
    # 更新设置
    launcher.settings["server_host"] = args.host
    launcher.settings["server_port"] = args.port
    
    if args.list:
        installations = launcher.detector.detect_houdini_installations()
        if installations:
            print("检测到的Houdini安装:")
            for inst in installations:
                print(f"- {inst['name']} (版本: {inst['version']})")
                print(f"  路径: {inst['path']}")
                print(f"  Python: {inst['python_path']}")
                print()
        else:
            print("未检测到Houdini安装")
        return
    
    if args.houdini_path:
        # 手动指定路径
        if os.path.exists(args.houdini_path):
            python_path = launcher.detector._find_houdini_python(args.houdini_path)
            if python_path:
                installation = {
                    "name": f"手动指定 - {os.path.basename(args.houdini_path)}",
                    "path": args.houdini_path,
                    "python_path": python_path,
                    "version": "Manual"
                }
                launcher.settings["selected_installation"] = installation
                launcher.save_settings()
            else:
                print(f"在指定路径中未找到Python可执行文件: {args.houdini_path}")
                return
        else:
            print(f"指定的Houdini路径不存在: {args.houdini_path}")
            return
    
    if args.auto:
        # 自动模式：使用已保存的设置
        if not launcher.settings.get("selected_installation"):
            print("自动模式需要先配置Houdini安装")
            installations = launcher.detector.detect_houdini_installations()
            if installations:
                launcher.select_houdini_installation(installations)
            else:
                print("未检测到Houdini安装，请手动指定路径")
                return
    
    # 启动服务器
    launcher.start_server()


if __name__ == "__main__":
    main() 