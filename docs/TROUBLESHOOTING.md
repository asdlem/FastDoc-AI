# FastAgent 故障排除指南

本文档提供了FastAgent系统可能遇到的常见问题和对应的解决方案。

## 目录

- [启动问题](#启动问题)
  - [后端启动失败](#后端启动失败)
  - [前端启动失败](#前端启动失败)
- [连接问题](#连接问题)
  - [前端连接后端失败](#前端连接后端失败)
  - [MCP服务连接失败](#mcp服务连接失败)
- [登录问题](#登录问题)
  - [无法登录](#无法登录)
  - [token过期或无效](#token过期或无效)
- [聊天功能问题](#聊天功能问题)
  - [无法发送消息](#无法发送消息)
  - [响应超时](#响应超时)
  - [加载中状态卡住](#加载中状态卡住)
- [环境配置问题](#环境配置问题)
  - [Python依赖问题](#python依赖问题)
  - [Node.js依赖问题](#nodejs依赖问题)
- [日志和调试](#日志和调试)

## 启动问题

### 后端启动失败

**症状**: 运行`start.bat`后显示错误或者服务无法启动。

**可能原因和解决方案**:

1. **端口被占用**

   **错误信息**: `[错误] 端口 8002 已被占用！`
   
   **解决方法**:
   ```powershell
   # 查找占用端口的进程
   netstat -ano | findstr :8002
   
   # 终止进程（替换PID为实际进程ID）
   taskkill /F /PID <PID>
   ```

2. **虚拟环境问题**

   **错误信息**: `无法找到python解释器` 或 `无法激活虚拟环境`
   
   **解决方法**:
   ```powershell
   # 重新创建虚拟环境
   rmdir /s /q .venv311
   python -m venv .venv311
   .venv311\Scripts\activate
   pip install -r requirements.txt
   ```

3. **配置文件错误**

   **错误信息**: `无法解析配置文件` 或 `配置文件不存在`
   
   **解决方法**:
   - 确保`fastagent.config.yaml`和`fastagent.secrets.yaml`位于项目根目录
   - 检查YAML语法是否正确（缩进、冒号等）
   - 运行`setup.bat`重新生成配置文件模板

4. **Python模块缺失**

   **错误信息**: `ImportError: No module named xxx`
   
   **解决方法**:
   ```powershell
   # 确认虚拟环境激活
   .venv311\Scripts\activate
   
   # 重新安装依赖
   pip install -r requirements.txt
   ```

### 前端启动失败

**症状**: 运行`start-frontend.bat`后显示错误或者前端无法启动。

**可能原因和解决方案**:

1. **端口被占用**

   **错误信息**: `[警告] 端口 3000 已被占用!`
   
   **解决方法**:
   ```powershell
   # 查找占用端口的进程
   netstat -ano | findstr :3000
   
   # 终止进程
   taskkill /F /PID <PID>
   ```

2. **Node.js版本不兼容**

   **错误信息**: `Error: The module 'xxx' was compiled against a different Node.js version`
   
   **解决方法**:
   - 安装Node.js 18.0+版本
   - 清理并重新安装依赖：
     ```powershell
     cd v0-frontend
     rmdir /s /q node_modules
     del package-lock.json
     npm install --legacy-peer-deps
     ```

3. **依赖安装不完整**

   **错误信息**: `Cannot find module 'xxx'` 或 `Module not found`
   
   **解决方法**:
   ```powershell
   cd v0-frontend
   npm install --force --legacy-peer-deps
   ```

## 连接问题

### 前端连接后端失败

**症状**: 前端界面显示"无法连接到服务器"或API请求失败。

**可能原因和解决方案**:

1. **后端服务未运行**

   **解决方法**:
   - 确认后端服务正在运行
   - 检查端口是否正确（默认8002）
   - 运行`start.bat`启动后端服务

2. **CORS配置问题**

   **错误信息**: `Access to fetch at 'xxx' from origin 'xxx' has been blocked by CORS policy`
   
   **解决方法**:
   - 检查后端CORS配置是否正确
   - 确保前端请求的URL与后端配置的CORS允许源匹配

3. **网络问题**

   **解决方法**:
   - 检查防火墙设置
   - 确认localhost或127.0.0.1可以正常访问

### MCP服务连接失败

**症状**: 发送消息后无响应或报错"MCP服务连接失败"。

**可能原因和解决方案**:

1. **配置错误**

   **解决方法**:
   - 检查`fastagent.secrets.yaml`中的MCP服务URL是否正确
   - 确认MCP服务器是否可用

2. **网络问题**

   **解决方法**:
   - 检查网络连接
   - 确认能够访问MCP服务URL
   - 检查防火墙或代理设置

3. **SSE连接问题**

   **解决方法**:
   - 重启后端服务
   - 检查日志中SSE连接的错误信息

## 登录问题

### 无法登录

**症状**: 尝试登录时显示"用户名或密码错误"或无法通过认证。

**可能原因和解决方案**:

1. **用户不存在**

   **解决方法**:
   - 确认用户已注册
   - 使用正确的用户名
   - 如果是新系统，使用默认的管理员账户（通常是admin/admin123）

2. **密码错误**

   **解决方法**:
   - 确认输入了正确的密码
   - 如果忘记密码，尝试使用默认管理员账户
   - 如果仍有问题，可以直接修改数据库：
     ```sql
     -- 使用SQLite工具打开数据库
     UPDATE users SET hashed_password = 'your_new_hashed_password' WHERE username = 'your_username';
     ```

3. **数据库问题**

   **解决方法**:
   - 检查`data`目录中的SQLite数据库文件是否存在
   - 确认数据库权限正确
   - 如果数据库损坏，可能需要重新创建：
     ```powershell
     del data\fastapi.db
     # 重启服务会自动创建新数据库
     ```

### token过期或无效

**症状**: 登录成功后很快就被退出，或收到"token无效"的错误。

**可能原因和解决方案**:

1. **token过期**

   **解决方法**:
   - 重新登录获取新token
   - 检查后端配置中的token过期时间设置
   - 在`app/core/security.py`中增加token有效期

2. **JWT密钥变更**

   **解决方法**:
   - 确保后端服务没有重启或重新生成密钥
   - 检查`app/core/config.py`中的SECRET_KEY配置

## 聊天功能问题

### 无法发送消息

**症状**: 点击发送按钮后没有响应，或消息无法发送。

**可能原因和解决方案**:

1. **前后端连接问题**

   **解决方法**:
   - 检查网络连接
   - 确认后端服务正在运行
   - 查看浏览器开发者工具中的网络请求和响应

2. **会话ID问题**

   **解决方法**:
   - 尝试创建新会话
   - 确认当前会话ID有效

3. **认证问题**

   **解决方法**:
   - 检查token是否有效
   - 重新登录获取新token

### 响应超时

**症状**: 发送消息后长时间没有响应，最终显示超时错误。

**可能原因和解决方案**:

1. **MCP服务响应慢**

   **解决方法**:
   - 检查MCP服务器状态
   - 增加超时设置值：
     - 在发送查询时增加`timeout`参数
     - 修改`app/services/agent_service.py`中的超时设置

2. **复杂查询处理时间长**

   **解决方法**:
   - 尝试发送更简单的查询
   - 增加超时时间限制
   - 在`app/api/endpoints/sessions.py`中增加请求超时配置

### 加载中状态卡住

**症状**: 发送消息后界面一直显示"加载中"状态。

**可能原因和解决方案**:

1. **响应处理错误**

   **解决方法**:
   - 检查后端日志中是否有错误信息
   - 刷新页面或重新启动前端应用
   - 确认MCP服务正常工作

2. **前端状态管理问题**

   **解决方法**:
   - 清除浏览器缓存和Cookie
   - 重新登录
   - 如果问题持续，检查前端代码中的状态管理逻辑

## 环境配置问题

### Python依赖问题

**症状**: 安装依赖时出现错误，或运行时报缺少模块。

**可能原因和解决方案**:

1. **版本冲突**

   **错误信息**: `xxx has requirement xxx, but you'll have xxx which is incompatible`
   
   **解决方法**:
   ```powershell
   pip install -r requirements.txt --ignore-installed
   ```

2. **安装失败**

   **解决方法**:
   - 使用国内镜像源：
     ```powershell
     pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
     ```
   - 单独安装问题依赖：
     ```powershell
     pip install problematic_package==version
     ```

3. **虚拟环境激活问题**

   **解决方法**:
   - 确认使用了正确的激活命令
   - Windows PowerShell可能需要更改执行策略：
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

### Node.js依赖问题

**症状**: 前端依赖安装失败或运行时报错。

**可能原因和解决方案**:

1. **依赖冲突**

   **错误信息**: `npm ERR! code ERESOLVE`
   
   **解决方法**:
   ```powershell
   npm install --legacy-peer-deps --force
   ```

2. **Node.js版本不兼容**

   **解决方法**:
   - 安装Node.js 18.0+版本
   - 使用nvm管理多个Node.js版本：
     ```powershell
     nvm install 18
     nvm use 18
     ```

3. **npm缓存问题**

   **解决方法**:
   ```powershell
   npm cache clean --force
   npm install
   ```

## 日志和调试

FastAgent提供了详细的日志记录，可以帮助排查问题：

1. **查看后端日志**:
   - 日志文件位于`logs/app.log`
   - 查看日志中的错误和警告信息

2. **调整日志级别**:
   - 在`fastagent.config.yaml`中修改日志级别：
     ```yaml
     logger:
       level: "debug"  # 改为debug获取更详细日志
     ```

3. **前端调试**:
   - 使用浏览器开发者工具查看网络请求和控制台错误
   - 在Next.js开发模式下可以看到详细的错误信息

4. **API调试**:
   - 使用Postman或curl测试API端点：
     ```powershell
     curl -X POST http://localhost:8002/api/users/token -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
     ```

5. **数据库检查**:
   - 使用SQLite浏览器工具查看数据库内容
   - 检查用户表、会话表和消息表的记录

如果以上解决方案无法解决您的问题，请收集相关日志信息并联系技术支持团队。 