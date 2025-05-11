@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0\..\..\"
chcp 65001 >nul

echo ======================================
echo    FastAgent 前端依赖安装
echo ======================================
echo.

rem 检查Node.js安装
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo [错误] 未检测到Node.js
  echo 下载地址: https://nodejs.org/
  exit /b 1
)

rem 进入前端目录
cd v0-frontend

rem 检查是否需要清理
if exist "node_modules" (
  echo [信息] 已检测到node_modules目录
  set /p CLEAN_OPTION="是否清理现有依赖并重新安装? (Y/N): "
  if /i "!CLEAN_OPTION!"=="Y" (
    echo [清理] 正在删除现有依赖...
    rmdir /s /q node_modules
    if exist "package-lock.json" del /f /q package-lock.json
    echo 清理完成!
  ) else (
    echo [信息] 保留现有依赖，跳过安装步骤...
    goto :SKIP_INSTALL
  )
)

rem 安装依赖
echo [安装] 正在安装前端依赖...
echo 这可能需要几分钟时间，请耐心等待...

call npm install --legacy-peer-deps

if %ERRORLEVEL% NEQ 0 (
  echo.
  echo [警告] 使用--legacy-peer-deps参数安装失败
  echo 尝试使用--force参数重新安装...
  call npm install --force
  
  if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 依赖安装仍然失败
    echo.
    echo 可能的解决方案:
    echo  1. 确保Node.js版本 ≥ 18.0.0
    echo  2. 确保网络连接正常
    echo  3. 尝试手动执行: cd v0-frontend ^& npm install --force
    echo  4. 检查package.json文件是否有错误
    echo.
    cd ..
    exit /b 1
  )
)

:SKIP_INSTALL

echo.
echo ======================================
echo    前端依赖安装完成!
echo ======================================
echo 现在您可以运行 start-frontend.bat 启动前端服务
echo.

cd .. 