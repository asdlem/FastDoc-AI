@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0\..\..\"
chcp 65001 >nul

echo ======================================
echo       FastAgent 前端服务启动
echo ======================================
echo.

rem 检查Node.js安装
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo [错误] 未检测到Node.js
  echo 下载地址: https://nodejs.org/
  exit /b 1
)

rem 检查前端端口是否被占用
set PORT=3000
set PORT_IN_USE=0
netstat -ano | findstr ":%PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  set PORT_IN_USE=1
)

if %PORT_IN_USE% EQU 1 (
  echo [警告] 端口 %PORT% 已被占用!
  echo 请关闭使用此端口的程序后重试。
  exit /b 1
)

rem 检查后端服务是否运行
set BACKEND_PORT=8002
set BACKEND_RUNNING=0
netstat -ano | findstr ":%BACKEND_PORT% .*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  set BACKEND_RUNNING=1
  echo [信息] 已检测到后端服务运行中
) else (
  echo [警告] 未检测到后端服务！
  echo [信息] 正在尝试自动启动后端服务...
  
  start cmd /c "scripts\bat\start.bat"
  
  echo [信息] 已启动后端服务，等待10秒使其初始化...
  timeout /t 10 /nobreak >nul
)

rem 进入前端目录
cd v0-frontend

rem 检查依赖
if not exist "node_modules" (
  echo [信息] 未找到前端依赖，正在安装...
  echo 这可能需要几分钟时间，请耐心等待...
  
  call npm install --legacy-peer-deps
  
  if %ERRORLEVEL% NEQ 0 (
    echo [信息] 使用--legacy-peer-deps安装失败，尝试使用--force参数...
    call npm install --force
    
    if %ERRORLEVEL% NEQ 0 (
      echo [错误] 前端依赖安装失败，请尝试手动运行安装命令:
      echo cd v0-frontend ^& npm install --force
      cd ..
      exit /b 1
    )
  )
  
  echo [信息] 依赖安装完成
) else (
  echo [信息] 前端依赖已安装
)

echo.
echo [启动] FastAgent前端服务(端口: %PORT%)
echo 访问地址: http://localhost:%PORT%
echo 按Ctrl+C终止服务
echo.

rem 启动开发服务器
call npm run dev -- --port %PORT%

endlocal
cd .. 