@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
chcp 65001 >nul

echo ======================================
echo       FastAgent 一键启动
echo ======================================
echo.

echo [信息] 正在启动FastAgent后端服务...
start cmd /k "title FastAgent后端服务 & scripts\bat\start.bat"

echo [信息] 等待后端启动...
set /a retry_count=0
set /a max_retries=30

:check_backend
timeout /t 2 /nobreak >nul
set /a retry_count+=1
echo [信息] 检查后端服务状态 (尝试 %retry_count%/%max_retries%)...
powershell -command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8002/health' -UseBasicParsing -TimeoutSec 2; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    echo [成功] 后端服务已启动!
    goto start_frontend
)
if %retry_count% LSS %max_retries% goto check_backend
echo [警告] 后端服务可能未正确启动，但仍将尝试启动前端服务...

:start_frontend
echo [信息] 正在启动FastAgent前端服务...
start cmd /k "title FastAgent前端服务 & scripts\bat\start-frontend.bat"

echo [信息] 等待前端启动...
set /a retry_count=0

:check_frontend
timeout /t 2 /nobreak >nul
set /a retry_count+=1
echo [信息] 检查前端服务状态 (尝试 %retry_count%/%max_retries%)...
powershell -command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing -TimeoutSec 2; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if %ERRORLEVEL% EQU 0 (
    echo [成功] 前端服务已启动!
    goto all_started
)
if %retry_count% LSS %max_retries% goto check_frontend
echo [警告] 前端服务可能未正确启动，请手动检查...

:all_started
echo.
echo [信息] FastAgent 启动状态:
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8002/docs
echo.
echo 注意: 服务已在独立的命令窗口中运行，关闭这些窗口将停止对应服务。
echo.

endlocal 