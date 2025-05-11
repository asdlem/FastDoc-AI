@echo off
cd /d "%~dp0\..\..\"
chcp 65001 >nul

echo ======================================
echo       FastAgent 环境设置
echo ======================================
echo.

rem 创建虚拟环境
if not exist ".venv311\Scripts\activate.bat" (
  echo [1/4] 创建Python虚拟环境...
  python -m venv .venv311
) else (
  echo [1/4] 虚拟环境已存在，跳过创建
)

rem 激活虚拟环境
call .venv311\Scripts\activate.bat

rem 安装依赖
echo [2/4] 安装项目依赖...
pip install -r requirements.txt

rem 创建数据目录
echo [3/4] 创建必要的目录...
if not exist "data" mkdir data
if not exist "logs" mkdir logs

rem 检查并创建secrets配置文件
echo [4/4] 检查配置文件...
if not exist "fastagent.secrets.yaml" (
  echo 创建 fastagent.secrets.yaml 模板...
  (
    echo # FastAgent Secrets Configuration
    echo # WARNING: Keep this file secure and never commit to version control
    echo.
    echo # API密钥配置
    echo openai:
    echo     api_key: YOUR_OPENAI_API_KEY_HERE
    echo anthropic:
    echo     api_key: YOUR_ANTHROPIC_API_KEY_HERE
    echo deepseek:
    echo     api_key: YOUR_DEEPSEEK_API_KEY_HERE
    echo openrouter:
    echo     api_key: YOUR_OPENROUTER_API_KEY_HERE
    echo.
    echo # MCP服务器配置 - 敏感信息部分
    echo mcp:
    echo     servers:
    echo         context7-mcp:
    echo             url: "https://mcp.api-inference.modelscope.cn/sse/bc2e7904bb514b"
    echo         fetch:
    echo             url: "https://mcp.api-inference.modelscope.cn/sse/e594722f29c04a"
  ) > fastagent.secrets.yaml
  echo 已创建 fastagent.secrets.yaml 模板，请编辑该文件填入您的API密钥
) else (
  echo fastagent.secrets.yaml 已存在，跳过创建
)

echo.
echo ======================================
echo       环境设置完成!
echo ====================================== 