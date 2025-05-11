# FastAgent

<div align="center">
  <p>
    <em>现代化AI技术助手 - 基于大型语言模型的问答系统</em>
  </p>
  <p>
    <a href="#主要特性">主要特性</a> •
    <a href="#快速开始">快速开始</a> •
    <a href="#系统架构">系统架构</a> •
    <a href="#安装指南">安装指南</a> •
    <a href="#使用方法">使用方法</a> •
    <a href="#文档">文档</a> •
    <a href="#常见问题">常见问题</a>
  </p>
</div>

## 项目简介

FastAgent是一个基于FastAPI和MCP(Model Call Protocol)框架构建的AI技术助手系统。它能够利用大型语言模型(LLMs)的强大能力，为用户提供专业的技术问题解答、代码分析与编写帮助，以及智能文档生成等功能。

本项目采用前后端分离的架构，后端基于Python FastAPI构建RESTful API服务，前端使用Next.js和React打造现代化的用户界面，通过MCP框架与各种大型语言模型无缝集成。

## 主要特性

🚀 **强大的AI能力**
- 集成MCP框架接入先进大型语言模型
- 专业的技术问题解答与代码分析
- 智能文档生成与知识库查询

💻 **现代化用户界面**
- 响应式设计，适配各种设备
- 简洁直观的对话式交互
- Markdown格式支持，代码语法高亮

🔒 **安全与可靠**
- 多用户认证和权限管理
- 会话隔离与数据持久化
- 完整的错误处理和日志记录

🔌 **可扩展性**
- 模块化设计，易于扩展
- 支持多种大型语言模型的集成
- 可配置的系统提示词和参数

## 快速开始

### 系统要求

- **操作系统**: Windows 10/11
- **后端**: Python 3.9+
- **前端**: Node.js 18.0+
- **浏览器**: 现代浏览器 (Chrome, Firefox, Edge等)

### 一键安装与启动

使用以下命令快速启动FastAgent系统:

```powershell
# 克隆仓库（如果尚未克隆）
git clone https://github.com/yourusername/FastAgent.git
cd FastAgent

# 安装并启动全部服务
start-all.bat
```

成功启动后，浏览器将自动打开 http://localhost:3000，显示登录页面。

## 系统架构

FastAgent采用前后端分离的现代化架构:

```
┌────────────────┐      HTTP      ┌────────────────┐
│                │◄──────────────►│                │
│  前端应用      │                │  后端API服务   │
│  (Next.js)     │                │  (FastAPI)     │
│                │                │                │
└────────────────┘                └───────┬────────┘
                                          │
                                          │ HTTP/SSE
                                          ▼
                               ┌────────────────────┐
                               │                    │
                               │  大型语言模型服务  │
                               │  (MCP协议)         │
                               │                    │
                               └────────────────────┘
```

更多架构详情请参考[架构文档](docs/ARCHITECTURE.md)。

## 安装指南

### 自动安装（推荐）

FastAgent提供了多个自动化脚本，简化安装过程：

1. **完整安装**
   ```powershell
   setup.bat       # 后端环境设置
   build-frontend.bat  # 前端依赖安装
   ```

2. **分步安装**
   ```powershell
   # 1. 设置后端环境
   setup.bat
   
   # 2. 安装前端依赖
   build-frontend.bat
   ```

### 手动安装

如果自动脚本无法正常工作，可按照以下步骤手动安装：

1. **设置Python环境**
   ```powershell
   python -m venv .venv311
   .venv311\Scripts\activate
   pip install -r requirements.txt
   ```

2. **设置前端环境**
   ```powershell
   cd v0-frontend
   npm install --legacy-peer-deps
   cd ..
   ```

3. **配置文件设置**
   - 创建`fastagent.config.yaml`和`fastagent.secrets.yaml`文件
   - 参考`docs/INSTALLATION_GUIDE.md`中的配置说明

详细安装步骤请参考[安装指南](docs/INSTALLATION_GUIDE.md)。

## 使用方法

### 启动服务

1. **使用一键启动脚本（推荐）**
   ```powershell
   start-all.bat
   ```

2. **分别启动服务**
   ```powershell
   start.bat           # 启动后端服务
   start-frontend.bat  # 启动前端服务
   ```

### 基本使用流程

1. 访问 http://localhost:3000
2. 使用默认账户登录（用户名: admin，密码: admin123）
3. 创建新的会话或选择现有会话
4. 在对话框中输入技术问题
5. 等待系统生成回答

### API使用

FastAgent提供了完整的RESTful API，可通过以下步骤使用：

1. 获取认证Token
   ```
   POST /api/users/token
   ```

2. 创建会话
   ```
   POST /api/sessions/
   ```

3. 发送查询
   ```
   POST /api/sessions/query
   ```

详细API文档请参考[API参考文档](docs/API_REFERENCE.md)。

## 文档

FastAgent提供了全面的文档，帮助您更好地使用和开发系统：

- [安装指南](docs/INSTALLATION_GUIDE.md) - 详细的安装和配置说明
- [API参考文档](docs/API_REFERENCE.md) - 完整的API端点与使用示例
- [系统架构](docs/ARCHITECTURE.md) - 系统架构与组件说明
- [故障排除](docs/TROUBLESHOOTING.md) - 常见问题解决方案

## 常见问题

### 无法启动服务怎么办？

检查端口占用情况，确保8002（后端）和3000（前端）端口未被占用。可以使用以下命令检查：

```powershell
netstat -ano | findstr :8002
netstat -ano | findstr :3000
```

如需更多帮助，请参考[故障排除指南](docs/TROUBLESHOOTING.md)。

### 如何配置API密钥?

编辑`fastagent.secrets.yaml`文件，添加您的API密钥：

```yaml
deepseek:
    api_key: "YOUR_API_KEY_HERE"
```

### 如何自定义系统提示词?

系统提示词定义在`app/services/agent_service.py`文件中，可根据需要修改。

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于:

- 提交Bug报告和功能请求
- 改进文档和示例
- 提交代码改进和新功能

## 许可证

本项目采用MIT许可证 - 详见LICENSE文件。

## 致谢

FastAgent的开发得益于以下开源项目:

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Next.js](https://nextjs.org/) - React前端框架
- [MCP](https://github.com/mcp) - Model Call Protocol框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包和ORM

---

<div align="center">
  <p>
    <sub>Made with ❤️ by FastAgent团队</sub>
  </p>
</div> 