@echo off
setlocal

REM 获取当前脚本所在的目录
set "SCRIPT_DIR=%~dp0"

REM 设置Python解释器的路径
set "PYTHON_EXEC=%SCRIPT_DIR%venv\Python37\python.exe"

REM 设置要执行的Python脚本的路径
set "PYTHON_SCRIPT=%SCRIPT_DIR%main.py"

REM 执行Python脚本
"%PYTHON_EXEC%" "%PYTHON_SCRIPT%"

endlocal
