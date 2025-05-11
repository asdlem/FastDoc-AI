@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0\..\..\"
chcp 65001 >nul

echo ======================================
echo       FastAgent 后端服务启动
echo ======================================
echo.

rem 检查端口是否被占用
set PORT=8002
set PORT_IN_USE=0
netstat -ano | findstr ":%PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  set PORT_IN_USE=1
)

if %PORT_IN_USE% EQU 1 (
  echo [错误] 端口 %PORT% 已被占用！
  echo 可能FastAgent服务已经在运行，或者其他应用程序正在使用此端口。
  echo 如需强行重启，请先关闭占用端口的程序。
  exit /b 1
)

rem 检查虚拟环境
if not exist ".venv311\Scripts\activate.bat" (
  echo [信息] 虚拟环境未设置，正在自动设置...
  call scripts\bat\setup.bat
  if %ERRORLEVEL% NEQ 0 (
    echo [错误] 环境设置失败，请手动运行 setup.bat 进行配置。
    exit /b 1
  )
) else (
  echo [信息] 检测到虚拟环境
)

rem 激活虚拟环境
call .venv311\Scripts\activate.bat

rem 检查配置文件
if not exist "fastagent.secrets.yaml" (
  echo [警告] 未找到 fastagent.secrets.yaml 配置文件
  echo 正在自动创建配置模板...
  call scripts\bat\setup.bat
  
  echo.
  echo [重要] 请编辑 fastagent.secrets.yaml 文件填入您的API密钥！
  echo 按任意键继续...
  pause >nul
)

echo [启动] 正在启动FastAgent后端服务(端口: %PORT%)...
echo 按 Ctrl+C 可以终止服务
echo.

rem 启动服务器
python main.py

endlocal 