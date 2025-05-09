# AI文档助手

这是一个基于 fast-agent 和 FastAPI 构建的高性能 AI 代理 Web 服务，提供了一个简洁易用的 RESTful API 接口，使用 Model Completion Protocol (MCP) 实现了强大的 AI 文档助手功能。本项目专为需要快速集成大语言模型功能的应用设计，解决了传统实现中的异步处理问题。

## 特性

- **强大的 AI 代理**: 基于 fast-agent 框架，支持复杂的多工具交互
- **RESTful API**: 简洁的 API 设计，易于集成到各种应用场景
- **MCP 工具支持**: 内置 fetch 和 context7 工具，提供强大的网页抓取和文档查询能力
- **高性能异步处理**: 使用 FastAPI 和 Uvicorn，原生支持异步操作
- **自动 URL 处理**: 自动检测并解析查询中的 URL，增强响应质量
- **结构化响应**: 返回清晰格式化的 Markdown 响应，便于前端展示
- **现代化 UI 界面**: 提供基于 React 和 Material UI 的 Google 风格聊天界面

## 系统要求

- Python 3.10+
- Windows 10/11 或 WSL2
- Docker (用于运行 MCP 服务器)
- Node.js 16+ 和 NPM 7+ (用于前端和 context7 MCP 服务器)

## 安装

### 创建虚拟环境

```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# 错误示例（Linux/macOS风格）
# source venv/bin/activate

# 正确示例（Windows PowerShell）
.\venv\Scripts\Activate.ps1
```

### 安装依赖

```powershell
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
cd ..
```

## 配置

### 配置文件

项目使用以下两个主要配置文件：

1. **fastagent.config.yaml** - 主配置文件
2. **fastagent.secrets.yaml** - 敏感信息配置文件（需要自行创建）

#### fastagent.secrets.yaml 示例

```yaml
# FastAgent Secrets Configuration
# WARNING: 保持此文件安全并且永远不要提交到版本控制系统

# 可以设置API密钥
openai:
    api_key: <your-openai-api-key-here>
anthropic:
    api_key: <your-anthropic-api-key-here>
deepseek:
    api_key: <your-deepseek-api-key-here>
openrouter:
    api_key: <your-openrouter-api-key-here>

# MCP服务器环境变量
mcp:
    servers:
        brave:
            env:
                BRAVE_API_KEY: <your_brave_api_key_here>
```

#### fastagent.config.yaml 示例

```yaml
default_api: deepseek
default_model: deepseek-chat

apis:
  deepseek:
    protocol: http
    api_key_env: DEEPSEEK_API_KEY
    base_url: "https://api.deepseek.com/v1"

clients:
  default:
    api: deepseek
    model: "deepseek-chat"

logger:
    progress_display: false  # 关闭进度条
    show_chat: true  # 显示聊天消息
    show_tools: true  # 显示工具调用
    truncate_tools: true  # 截断长工具响应

# MCP Servers
mcp:
    servers:
        fetch:
            command: "docker"
            args: ["run", "-i", "--rm", "mcp/fetch"]
        context7:
            command: "npx"
            args: ["-y", "@upstash/context7-mcp@latest"]
```

### MCP 环境要求

本项目使用 Model Completion Protocol (MCP) 服务器扩展 AI 代理功能：

1. **Docker 环境**：
   - 安装 Docker Desktop 或 Docker Engine
   - 拉取所需容器：`docker pull mcp/fetch`

2. **Node.js 环境**：
   - 安装 Node.js 和 NPM
   - 用于运行 context7 MCP 服务器

3. **权限与网络**：
   - Docker 需要足够的权限运行容器
   - 确保网络访问权限（用于fetch和context7等MCP服务）

## 快速开始

### 1. 创建配置文件

在项目根目录创建 `fastagent.secrets.yaml` 并配置您的API密钥

### 2. 启动后端服务

```powershell
# 错误示例（Linux风格）
# python app.py &

# 正确示例（Windows PowerShell）
python fastapp.py
```

后端服务将在 `http://localhost:5000` 启动

### 3. 启动前端服务

```powershell
# 进入前端目录
cd frontend

# 开发模式启动
npm run dev

# 如果需要构建生产版本
# npm run build
# npm run preview
```

前端应用将在 `http://localhost:3000` 启动

### 4. API 使用示例

```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    "query" = "如何使用Python实现异步函数？"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/query" -Method Post -Headers $headers -Body $body
```

### 5. URL 引用功能

可以在查询中包含URL，系统会自动处理：

```powershell
$body = @{
    "query" = "分析这篇文章的主要观点 @https://example.com/article"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/query" -Method Post -Headers $headers -Body $body
```

## 项目结构

```
FastAgent/
│
├── fastapp.py                   # 后端主应用入口
├── requirements.txt             # 后端项目依赖
├── README.md                    # 项目说明
├── fastagent.config.yaml        # MCP服务器配置
├── fastagent.secrets.yaml       # API密钥配置（不提交到Git）
└── frontend/                    # 前端项目目录
    ├── src/                     # 前端源代码
    │   ├── api/                 # API请求服务
    │   ├── components/          # 可复用组件
    │   ├── context/             # React上下文
    │   ├── pages/               # 页面组件 
    │   ├── styles/              # CSS样式
    │   └── utils/               # 工具函数
    ├── public/                  # 静态资源
    ├── package.json             # 前端依赖配置
    └── vite.config.js           # Vite配置
```

## 前端功能

- **Google风格UI**: 采用Modern Material Design风格的用户界面
- **响应式设计**: 适配桌面和移动设备的布局
- **MD渲染**: 支持Markdown渲染和代码语法高亮
- **会话管理**: 侧边栏历史对话列表和新会话创建
- **实时反馈**: 加载状态指示和错误处理
- **URL集成**: 支持提交带URL的查询并获取分析结果

## 常见问题

### Q: 应用启动时出现"event loop is already running"错误？
A: 确保使用最新版本的 fast-agent 库，该版本已处理事件循环问题。

### Q: 如何修改监听端口？
A: 编辑 fastapp.py 文件中的 uvicorn.run 参数。

### Q: 前端无法连接到后端API？
A: 检查frontend/src/config.js中的API_BASE_URL配置是否与后端服务地址一致。

### Q: MCP服务器启动失败？
A: 检查相应的环境是否已安装（Docker或Node.js）以及网络连接是否正常。

## 贡献指南

欢迎提交 Pull Request 或创建 Issue 来改进项目。

## 许可证

[MIT](https://choosealicense.com/licenses/mit/) 