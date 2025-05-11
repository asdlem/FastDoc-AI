from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, root_validator

# 用户基础模型
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True

# 创建用户请求模型
class UserCreate(UserBase):
    password: str
    
    @validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3:
            raise ValueError('用户名长度必须至少为3个字符')
        return v
    
    @validator('password')
    def password_must_be_valid(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度必须至少为6个字符')
        return v

# 登录请求模型
class UserLogin(BaseModel):
    username: str
    password: str

# 令牌响应模型
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 令牌数据模型
class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

# 用户更新模型
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

# 用户响应模型
class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 用户模式
class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDB):
    pass

# 聊天消息模式
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    @validator('role')
    def role_must_be_valid(cls, v):
        valid_roles = ['user', 'assistant', 'system']
        if v not in valid_roles:
            raise ValueError(f'角色必须为: {", ".join(valid_roles)}')
        return v

class Message(MessageBase):
    id: int
    session_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 聊天会话模式
class ChatSessionBase(BaseModel):
    title: str = "新会话"
    is_active: bool = True

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None

class ChatSessionList(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    class Config:
        from_attributes = True

class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List = []
    
    class Config:
        from_attributes = True 