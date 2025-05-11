import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.user_service import (
    get_user_by_id, get_user_by_username, get_user_by_email,
    create_user, authenticate_user, update_user, delete_user,
    get_users, create_initial_admin
)
from app.core.security import get_password_hash, verify_password

class TestUserService(unittest.TestCase):
    """用户服务单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.db = MagicMock(spec=Session)
        self.test_user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_admin=False
        )
        
    def test_get_user_by_id(self):
        """测试通过ID获取用户"""
        self.db.query.return_value.filter.return_value.first.return_value = self.test_user
        user = get_user_by_id(self.db, 1)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, "testuser")
        self.db.query.assert_called_once_with(User)
        
    def test_get_user_by_username(self):
        """测试通过用户名获取用户"""
        self.db.query.return_value.filter.return_value.first.return_value = self.test_user
        user = get_user_by_username(self.db, "testuser")
        self.assertEqual(user.username, "testuser")
        self.db.query.assert_called_once_with(User)
        
    def test_get_user_by_email(self):
        """测试通过邮箱获取用户"""
        self.db.query.return_value.filter.return_value.first.return_value = self.test_user
        user = get_user_by_email(self.db, "test@example.com")
        self.assertEqual(user.email, "test@example.com")
        self.db.query.assert_called_once_with(User)
        
    def test_create_user(self):
        """测试创建用户"""
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()
        
        result = create_user(
            self.db, 
            username="newuser", 
            email="new@example.com", 
            password="password123"
        )
        
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once()
        self.assertEqual(result.username, "newuser")
        self.assertEqual(result.email, "new@example.com")
        self.assertTrue(result.hashed_password)
        
    @patch('app.services.user_service.verify_password')
    def test_authenticate_user_success(self, mock_verify):
        """测试用户认证成功"""
        mock_verify.return_value = True
        self.db.query.return_value.filter.return_value.first.return_value = self.test_user
        
        user = authenticate_user(self.db, "testuser", "password123")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        
    @patch('app.services.user_service.verify_password')
    def test_authenticate_user_wrong_password(self, mock_verify):
        """测试用户认证失败 - 密码错误"""
        mock_verify.return_value = False
        self.db.query.return_value.filter.return_value.first.return_value = self.test_user
        
        user = authenticate_user(self.db, "testuser", "wrongpassword")
        self.assertIsNone(user)
        
    def test_authenticate_user_no_user(self):
        """测试用户认证失败 - 用户不存在"""
        self.db.query.return_value.filter.return_value.first.return_value = None
        
        user = authenticate_user(self.db, "nonexistent", "password123")
        self.assertIsNone(user)
        
    def test_update_user(self):
        """测试更新用户"""
        self.db.query.return_value.filter.return_value.first.return_value = self.test_user
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()
        
        updated_user = update_user(
            self.db, 
            1, 
            username="updateduser",
            email="updated@example.com"
        )
        
        self.assertEqual(updated_user.username, "updateduser")
        self.assertEqual(updated_user.email, "updated@example.com")
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(self.test_user)
        
    def test_delete_user(self):
        """测试删除用户"""
        self.db.query.return_value.filter.return_value.first.return_value = self.test_user
        self.db.delete = MagicMock()
        self.db.commit = MagicMock()
        
        result = delete_user(self.db, 1)
        
        self.assertTrue(result)
        self.db.delete.assert_called_once_with(self.test_user)
        self.db.commit.assert_called_once()
        
    def test_delete_user_not_found(self):
        """测试删除不存在的用户"""
        self.db.query.return_value.filter.return_value.first.return_value = None
        
        result = delete_user(self.db, 999)
        
        self.assertFalse(result)
        
    def test_get_users(self):
        """测试获取用户列表"""
        mock_users = [self.test_user, MagicMock(spec=User)]
        self.db.query.return_value.offset.return_value.limit.return_value.all.return_value = mock_users
        
        users = get_users(self.db)
        
        self.assertEqual(len(users), 2)
        self.db.query.assert_called_once_with(User)
        
if __name__ == "__main__":
    unittest.main() 