@echo off
cd /d "%~dp0\..\..\"
chcp 65001 >nul

echo FastAgent API 测试
echo.

rem 激活虚拟环境
if exist ".venv311\Scripts\activate.bat" call .venv311\Scripts\activate.bat

rem 运行测试
python scripts/test/unified_test.py

pause 