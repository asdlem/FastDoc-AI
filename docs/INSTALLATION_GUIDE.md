# FastAgent 安装指南

本文档提供了安装和配置FastAgent系统的详细步骤，包括后端和前端组件。

## 目录

- [系统要求](#系统要求)
- [后端安装](#后端安装)
  - [基础环境配置](#基础环境配置)
  - [使用脚本安装](#使用脚本安装)
  - [手动安装步骤](#手动安装步骤)
  - [配置文件设置](#配置文件设置)
- [前端安装](#前端安装)
  - [Node.js环境设置](#nodejs环境设置)
  - [使用脚本安装](#使用脚本安装-1)
  - [手动安装步骤](#手动安装步骤-1)
- [验证安装](#验证安装)
- [启动服务](#启动服务)
- [常见问题](#常见问题)

## 系统要求

### 后端要求

- Windows 10/11 或 Linux 系统
- Python 3.9+ (推荐Python 3.11)
- pip 21.0+
- 至少2GB可用内存
- 至少1GB磁盘空间

### 前端要求

- Node.js 18.0+
- npm 8.0+ 或 yarn 1.22+
- 现代浏览器（Chrome, Firefox, Edge等）

## 后端安装

### 基础环境配置

1. 安装Python 3.9+：
   - Windows：从[Python官网](https://www.python.org/downloads/)下载并安装
   - 确保勾选"Add Python to PATH"选项

2. 验证Python安装：
   ```powershell
   python --version
   pip --version
   ```

### 使用脚本安装

FastAgent提供了自动化安装脚本，这是推荐的安装方式：

1. 打开命令提示符或PowerShell
2. 导航到项目根目录
3. 运行设置脚本：
   ```powershell
   setup.bat
   ```
   
脚本将自动执行以下操作：
- 创建Python虚拟环境
- 安装所需依赖
- 创建必要的数据目录
- 生成配置文件模板

### 手动安装步骤

如果自动脚本无法运行，可以按照以下步骤手动安装：

1. 创建Python虚拟环境：
   ```powershell
   python -m venv .venv311
   ```

2. 激活虚拟环境：
   ```powershell
   .venv311\Scripts\activate
   ```

3. 安装依赖：
   ```powershell
   pip install -r requirements.txt
   ```

4. 创建必要的目录：
   ```powershell
   mkdir data
   mkdir logs
   ```

5. 复制配置文件模板：
   - 创建`fastagent.config.yaml`和`fastagent.secrets.yaml`文件
   - 参考项目中的示例文件填写配置

### 配置文件设置

FastAgent使用两个主要配置文件：

1. **fastagent.config.yaml** - 常规配置：
   ```yaml
   # 默认模型
   default_model: deepseek-chat

   # DeepSeek API配置
   deepseek:
     base_url: "https://api.deepseek.com/v1"

   # 日志配置
   logger:
     type: "console"
     level: "info"
     progress_display: false
     show_chat: true
     show_tools: true
     truncate_tools: true

   # MCP服务器配置
   mcp:
     servers:
       context7-mcp:
         transport: "sse"
       fetch:
         transport: "sse"
   ```

2. **fastagent.secrets.yaml** - 敏感信息（API密钥等）：
   ```yaml
   # FastAgent Secrets Configuration
   # WARNING: Keep this file secure and never commit to version control

   # API密钥配置
   openai:
       api_key: YOUR_OPENAI_API_KEY_HERE
   anthropic:
       api_key: YOUR_ANTHROPIC_API_KEY_HERE
   deepseek:
       api_key: YOUR_DEEPSEEK_API_KEY_HERE
   openrouter:
       api_key: YOUR_OPENROUTER_API_KEY_HERE

   # MCP服务器配置 - 敏感信息部分
   mcp:
       servers:
           context7-mcp:
               url: "https://mcp.api-inference.modelscope.cn/sse/YOUR_MCP_ID"
           fetch:
               url: "https://mcp.api-inference.modelscope.cn/sse/YOUR_FETCH_MCP_ID"
   ```

> **重要提示**：请替换上述配置中的占位符为您的实际API密钥和配置信息。

## 前端安装

### Node.js环境设置

1. 安装Node.js 18.0+：
   - 从[Node.js官网](https://nodejs.org/)下载并安装LTS版本

2. 验证Node.js安装：
   ```powershell
   node --version
   npm --version
   ```

### 使用脚本安装

FastAgent提供了自动化前端安装脚本：

1. 导航到项目根目录
2. 运行前端安装脚本：
   ```powershell
   build-frontend.bat
   ```

脚本将自动执行以下操作：
- 检查Node.js安装
- 安装前端依赖包

### 手动安装步骤

如果自动脚本无法运行，可以按照以下步骤手动安装前端：

1. 导航到前端目录：
   ```powershell
   cd v0-frontend
   ```

2. 安装依赖：
   ```powershell
   npm install --legacy-peer-deps
   ```

   如果遇到问题，尝试使用force参数：
   ```powershell
   npm install --force
   ```

## 验证安装

安装完成后，可以通过以下步骤验证安装是否成功：

1. 检查虚拟环境：
   ```powershell
   .venv311\Scripts\activate
   python -c "import fastapi, mcp_agent; print('环境检查正常')"
   ```

2. 检查前端依赖：
   ```powershell
   cd v0-frontend
   npm list react next
   ```

## 启动服务

### 一键启动（推荐）

使用一键启动脚本同时启动前端和后端服务：

```powershell
start-all.bat
```

### 分别启动

1. 启动后端服务：
   ```powershell
   start.bat
   ```
   后端服务将在 http://localhost:8002 上运行。

2. 启动前端服务：
   ```powershell
   start-frontend.bat
   ```
   前端服务将在 http://localhost:3000 上运行。

## 常见问题

### 端口冲突

如果端口8002或3000已被占用，您可以：
- 关闭占用端口的应用程序
- 修改`scripts/bat/start.bat`和`scripts/bat/start-frontend.bat`中的端口设置

### 依赖安装失败

如果依赖安装失败，尝试以下解决方案：

1. 检查网络连接
2. 使用国内镜像源：
   ```powershell
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```
3. 对于前端依赖，尝试：
   ```powershell
   npm install --force --legacy-peer-deps
   ```

### Python虚拟环境问题

如果虚拟环境激活失败：

1. 检查PowerShell执行策略：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
2. 尝试使用CMD代替PowerShell
3. 手动删除`.venv311`目录并重新创建

### 配置文件错误

如果在启动时看到配置相关错误：

1. 确保`fastagent.config.yaml`和`fastagent.secrets.yaml`位于项目根目录
2. 检查YAML格式是否正确（缩进、冒号等）
3. 确保提供了必要的API密钥 