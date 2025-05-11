from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_current_admin_user
from app.api.schemas import UserCreate, UserResponse, UserLogin, Token, UserUpdate
from app.core.database import get_db
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.services.user_service import (
    authenticate_user, create_user, get_user_by_email, 
    get_user_by_username, get_users, update_user, delete_user
)

router = APIRouter(tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """注册新用户"""
    # 检查用户名是否已存在
    db_user = get_user_by_username(db, user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已被注册")
        
    # 检查邮箱是否已存在
    db_user = get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="邮箱已被注册")
        
    # 创建新用户
    user = create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(user_data: UserLogin, db: Session = Depends(get_db)):
    """登录获取访问令牌"""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """更新当前用户信息"""
    # 检查用户名是否已存在
    if user_data.username and user_data.username != current_user.username:
        db_user = get_user_by_username(db, user_data.username)
        if db_user:
            raise HTTPException(status_code=400, detail="用户名已被注册")
    
    # 检查邮箱是否已存在
    if user_data.email and user_data.email != current_user.email:
        db_user = get_user_by_email(db, user_data.email)
        if db_user:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    # 普通用户不能修改自己的管理员状态
    update_data = user_data.dict(exclude_unset=True)
    if "is_admin" in update_data:
        del update_data["is_admin"]
        
    updated_user = update_user(db, current_user.id, **update_data)
    return updated_user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有用户（仅管理员）"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """获取指定用户（仅管理员）"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """更新指定用户（仅管理员）"""
    # 检查用户是否存在
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
        
    # 检查用户名是否已存在
    if user_data.username and user_data.username != db_user.username:
        existing_user = get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已被注册")
    
    # 检查邮箱是否已存在
    if user_data.email and user_data.email != db_user.email:
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="邮箱已被注册")
    
    update_data = user_data.dict(exclude_unset=True)
    updated_user = update_user(db, user_id, **update_data)
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_admin(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """删除指定用户（仅管理员）"""
    # 不能删除自己
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录的管理员账户")
        
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return None 