# FastAgent API 参考文档

此文档提供了FastAgent API的详细说明，包括所有可用的端点、请求/响应格式以及示例。

## 目录

- [认证API](#认证api)
  - [获取访问令牌](#获取访问令牌)
  - [注册新用户](#注册新用户)
- [会话API](#会话api)
  - [创建会话](#创建会话)
  - [获取会话列表](#获取会话列表)
  - [获取会话详情](#获取会话详情)
  - [发送查询](#发送查询)
  - [删除会话](#删除会话)
  - [清空会话消息](#清空会话消息)
- [消息API](#消息api)
  - [获取消息列表](#获取消息列表)
  - [删除消息](#删除消息)
- [错误处理](#错误处理)
- [前端开发规范](#前端开发规范)

## 认证API

### 获取访问令牌

用于用户登录并获取JWT访问令牌。

**端点**: `POST /api/users/token`

**请求体**:
```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "用户名"
}
```

**错误响应**:
- 401 Unauthorized: 认证失败

### 注册新用户

用于创建新用户账户。

**端点**: `POST /api/users/register`

**请求体**:
```json
{
  "username": "新用户名",
  "password": "密码",
  "email": "user@example.com"
}
```

**响应**:
```json
{
  "id": 2,
  "username": "新用户名",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2023-07-01T12:00:00"
}
```

**错误响应**:
- 400 Bad Request: 用户名已存在或请求格式错误

## 会话API

所有会话API端点需要在请求头中包含有效的访问令牌：
```
Authorization: Bearer {access_token}
```

### 创建会话

创建新的对话会话。

**端点**: `POST /api/sessions/`

**请求体**:
```json
{
  "title": "会话标题"
}
```

**响应**:
```json
{
  "id": 1,
  "title": "会话标题",
  "created_at": "2023-07-01T12:00:00",
  "updated_at": "2023-07-01T12:00:00",
  "user_id": 1
}
```

### 获取会话列表

获取当前用户的所有会话列表。

**端点**: `GET /api/sessions/`

**响应**:
```json
[
  {
    "id": 1,
    "title": "会话标题",
    "created_at": "2023-07-01T12:00:00",
    "updated_at": "2023-07-01T12:00:00",
    "user_id": 1,
    "message_count": 10
  },
  {
    "id": 2,
    "title": "另一个会话",
    "created_at": "2023-07-02T12:00:00",
    "updated_at": "2023-07-02T12:00:00",
    "user_id": 1,
    "message_count": 5
  }
]
```

### 获取会话详情

获取特定会话的详细信息，包括消息历史。

**端点**: `GET /api/sessions/{session_id}`

**路径参数**:
- `session_id`: 会话ID

**响应**:
```json
{
  "id": 1,
  "title": "会话标题",
  "created_at": "2023-07-01T12:00:00",
  "updated_at": "2023-07-01T12:00:00",
  "user_id": 1,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "用户问题",
      "created_at": "2023-07-01T12:01:00",
      "session_id": 1
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "助手回答",
      "created_at": "2023-07-01T12:01:30",
      "session_id": 1
    }
  ]
}
```

### 发送查询

向指定会话发送查询并获取回复。

**端点**: `POST /api/sessions/query`

**请求体**:
```json
{
  "session_id": 1,
  "query": "用户问题内容",
  "timeout": 60
}
```

**响应**:
```json
{
  "session_id": 1,
  "message": "助手的回答内容",
  "message_id": 4,
  "created_at": "2023-07-01T12:05:00"
}
```

### 删除会话

删除指定ID的会话及其所有消息。

**端点**: `DELETE /api/sessions/{session_id}`

**路径参数**:
- `session_id`: 要删除的会话ID

**响应**:
```json
{
  "success": true,
  "message": "会话已删除"
}
```

### 清空会话消息

清空指定会话中的所有消息，但保留会话本身。

**端点**: `DELETE /api/sessions/{session_id}/messages`

**路径参数**:
- `session_id`: 会话ID

**响应**:
```json
{
  "success": true,
  "message": "会话消息已清空"
}
```

## 消息API

### 获取消息列表

获取特定会话中的所有消息。

**端点**: `GET /api/messages/?session_id={session_id}`

**查询参数**:
- `session_id`: 会话ID

**响应**:
```json
[
  {
    "id": 1,
    "role": "user",
    "content": "用户问题",
    "created_at": "2023-07-01T12:01:00",
    "session_id": 1
  },
  {
    "id": 2,
    "role": "assistant",
    "content": "助手回答",
    "created_at": "2023-07-01T12:01:30",
    "session_id": 1
  }
]
```

### 删除消息

删除特定ID的消息。

**端点**: `DELETE /api/messages/{message_id}`

**路径参数**:
- `message_id`: 要删除的消息ID

**响应**:
```json
{
  "success": true,
  "message": "消息已删除"
}
```

## 错误处理

所有API端点在发生错误时将返回标准的错误响应格式：

```json
{
  "detail": {
    "message": "错误描述",
    "error_code": "ERROR_CODE",
    "status_code": 400
  }
}
```

常见错误代码：
- `AUTHENTICATION_ERROR`: 认证失败或令牌无效
- `PERMISSION_DENIED`: 没有权限执行操作
- `RESOURCE_NOT_FOUND`: 请求的资源不存在
- `VALIDATION_ERROR`: 请求数据验证失败
- `SERVER_ERROR`: 服务器内部错误

## 前端开发规范

### 设计风格

- 整体UI风格参考Google设计语言和Google AI Studio的对话界面
- 遵循Material Design设计原则
- 颜色方案：
  - 主色：#1a73e8（Google蓝）
  - 次色：#4285f4
  - 强调色：#ea4335（红）、#fbbc04（黄）、#34a853（绿）
  - 背景色：#f8f9fa
  - 文字颜色：#202124（主文本）、#5f6368（次要文本）

### 响应式设计

- 必须适配以下尺寸：
  - 桌面端：≥1200px
  - 平板：768px-1199px
  - 移动端：≤767px
- 移动端优先的设计方法
- 使用相对单位（rem, em, %, vh, vw）进行布局

### 交互规范

- 加载状态必须有明确指示（加载动画）
- 所有操作需提供明确的反馈
- 错误提示应当友好且提供恢复建议
- 重要操作需要确认对话框
- 按钮状态应当明显区分（常规、悬停、禁用）

### 文本规范

- 所有用户界面文本必须使用中文
- 按钮文本应简洁明了，一般不超过4个汉字
- 提示信息应当友好且具有指导性
- 错误信息应当准确描述问题并提供解决方案

### 对话界面规范

- 用户消息靠右显示，使用主色背景
- 助手回复靠左显示，使用浅色背景
- 时间戳应简洁（今天显示时间，非今天显示日期）
- 长回复应支持折叠/展开
- 代码块必须有语法高亮
- Markdown格式必须正确渲染 