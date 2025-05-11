import os
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import Base
from app.core.database import get_db
from app.services.user_service import create_user
from main import app

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class TestUserAPI(unittest.TestCase):
    """用户API接口测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建数据库表
        Base.metadata.create_all(bind=engine)
        
        # 创建测试客户端
        cls.client = TestClient(app)
        
        # 覆盖依赖项
        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
                
        app.dependency_overrides[get_db] = override_get_db
        
        # 创建测试用户
        db = TestingSessionLocal()
        cls.test_user = create_user(
            db=db,
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        cls.test_admin = create_user(
            db=db,
            username="admin",
            email="admin@example.com",
            password="admin123",
            is_admin=True
        )
        db.close()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 删除测试数据库
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    
    def test_register_user(self):
        """测试用户注册"""
        response = self.client.post(
            "/api/users/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "newuser")
        self.assertEqual(data["email"], "new@example.com")
        self.assertTrue(data["is_active"])
        self.assertFalse(data["is_admin"])
    
    def test_register_duplicate_username(self):
        """测试注册重复用户名"""
        response = self.client.post(
            "/api/users/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("用户名已被注册", response.text)
    
    def test_login(self):
        """测试用户登录"""
        response = self.client.post(
            "/api/users/token",
            data={
                "username": "testuser",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        
        # 保存token用于后续测试
        self.token = data["access_token"]
    
    def test_login_wrong_password(self):
        """测试登录密码错误"""
        response = self.client.post(
            "/api/users/token",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("用户名或密码错误", response.text)
    
    def test_get_me_without_token(self):
        """测试未授权获取当前用户信息"""
        response = self.client.get("/api/users/me")
        self.assertEqual(response.status_code, 401)
    
    def test_get_me_with_token(self):
        """测试授权获取当前用户信息"""
        # 先登录获取token
        login_response = self.client.post(
            "/api/users/token",
            data={
                "username": "testuser",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # 使用token获取用户信息
        response = self.client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
    
    def test_update_me(self):
        """测试更新当前用户信息"""
        # 先登录获取token
        login_response = self.client.post(
            "/api/users/token",
            data={
                "username": "testuser",
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # 更新用户信息
        response = self.client.put(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "updateduser",
                "email": "updated@example.com"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], "updateduser")
        self.assertEqual(data["email"], "updated@example.com")
    
    def test_admin_get_users(self):
        """测试管理员获取所有用户"""
        # 先登录获取admin token
        login_response = self.client.post(
            "/api/users/token",
            data={
                "username": "admin",
                "password": "admin123"
            }
        )
        token = login_response.json()["access_token"]
        
        # 获取用户列表
        response = self.client.get(
            "/api/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)  # 至少有两个用户
    
    def test_non_admin_get_users(self):
        """测试非管理员获取所有用户"""
        # 先登录获取普通用户token
        login_response = self.client.post(
            "/api/users/token",
            data={
                "username": "updateduser",  # 使用之前更新过的用户名
                "password": "password123"
            }
        )
        token = login_response.json()["access_token"]
        
        # 尝试获取用户列表
        response = self.client.get(
            "/api/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("权限不足", response.text)

if __name__ == "__main__":
    unittest.main() 