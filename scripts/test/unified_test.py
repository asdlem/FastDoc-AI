#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FastAgent API 统一测试脚本
此脚本测试所有API端点，包括用户认证、聊天会话、查询和SSE连接
"""

import requests
import json
import time
import sys
import uuid
import os
import asyncio
from datetime import datetime
import traceback

# 确保正确的控制台编码
if sys.platform.startswith('win'):
    # Windows平台设置控制台编码
    os.environ["PYTHONIOENCODING"] = "utf-8"
    # 尝试设置控制台代码页为UTF-8 (65001)
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except Exception:
        pass

# 导入日志模块
sys.path.append('.')
try:
    from app.core.logging import test_logger
except ImportError:
    import logging
    test_logger = logging.getLogger('FastAgentTest')
    test_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    test_logger.addHandler(handler)

# 添加MCP测试模块
try:
    from mcp_agent.core.fastagent import FastAgent
except ImportError:
    test_logger.warning("未找到mcp_agent模块，SSE连接测试将被跳过")
    FastAgent = None

# 配置
BASE_URL = "http://localhost:8002"
API_PREFIX = "/api"
TOKEN = None
SESSIONS = []
TEST_ID = os.environ.get('TEST_ID', uuid.uuid4().hex[:8])  # 测试ID，用于跟踪日志

# 颜色配置
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# 测试结果
TEST_RESULTS = {}

def print_color(msg, color=Colors.BLUE, log_level='info', with_logging=False):
    """带颜色打印信息并记录日志"""
    print(f"{color}{msg}{Colors.END}")
    if with_logging:
        if log_level == 'info':
            test_logger.info(f"[TEST:{TEST_ID}] {msg}")
        elif log_level == 'error':
            test_logger.error(f"[TEST:{TEST_ID}] {msg}")

def print_header(title):
    """打印测试标题"""
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER}{title}{Colors.END}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.END}\n")

def print_section(title):
    """打印分节标题"""
    print(f"\n{Colors.CYAN}--- {title} ---{Colors.END}\n")

def print_success(message):
    """打印成功消息"""
    print(f"{Colors.GREEN}[成功] {message}{Colors.END}")
    test_logger.info(f"[TEST:{TEST_ID}] [成功] {message}")

def print_error(message):
    """打印错误消息"""
    print(f"{Colors.RED}[失败] {message}{Colors.END}")
    test_logger.error(f"[TEST:{TEST_ID}] [失败] {message}")

def print_info(message):
    """打印信息消息"""
    print(f"{Colors.CYAN}[信息] {message}{Colors.END}")

def print_json(data):
    """打印JSON数据"""
    print(f"{Colors.YELLOW}{json.dumps(data, indent=2, ensure_ascii=False)}{Colors.END}")

def log_response(response, request_name):
    """记录API响应（仅记录错误）"""
    if response.status_code >= 400:
        try:
            error_data = response.json()
            test_logger.error(f"[TEST:{TEST_ID}] {request_name} - 错误: {error_data}")
        except:
            test_logger.error(f"[TEST:{TEST_ID}] {request_name} - 响应内容: {response.text}")

def get_headers():
    """获取带认证的请求头"""
    if TOKEN:
        return {
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
    return {"Content-Type": "application/json"}

#========================================
# 1. 健康检查测试
#========================================
def test_health():
    """测试健康检查端点"""
    print_section("健康检查测试")
    
    try:
        # 添加10秒超时，避免长时间等待
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print_info(f"健康检查响应: {response.status_code}")
        print_json(response.json())
        
        success = response.status_code == 200
        TEST_RESULTS['健康检查'] = '通过' if success else '失败'
        
        if success:
            print_success("健康检查成功")
            return True
        else:
            print_error(f"健康检查失败! 状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"健康检查请求异常: {e}")
        
        # 尝试不带API前缀访问
        try:
            print_info("尝试不带API前缀访问健康检查...")
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            
            if response.status_code == 200:
                print_success("健康检查成功")
                TEST_RESULTS['健康检查'] = '通过'
                return True
        except Exception as e2:
            print_error(f"再次尝试健康检查失败: {e2}")
        
        TEST_RESULTS['健康检查'] = '失败'
        return False

#========================================
# 2. 用户认证测试
#========================================
def login(username="admin", password="admin123"):
    """登录并获取令牌"""
    print_section("用户登录测试")
    
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{BASE_URL}{API_PREFIX}/users/token", json=login_data)
        log_response(response, "登录请求")
        
        if response.status_code == 200:
            global TOKEN
            TOKEN = response.json()["access_token"]
            print_success(f"登录成功! 获取到令牌: {TOKEN[:20]}...")
            TEST_RESULTS['用户登录'] = '通过'
            return True
        else:
            print_error(f"登录失败! 状态码: {response.status_code}")
            print_json(response.json())
            TEST_RESULTS['用户登录'] = '失败'
            return False
    except Exception as e:
        print_error(f"登录请求异常: {e}")
        TEST_RESULTS['用户登录'] = '失败'
        return False

def test_register_user(username, email, password):
    """测试注册用户"""
    print_section(f"注册用户测试 ({username})")
    
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/users/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        
        if response.status_code == 200:
            print_success(f"用户注册成功: {username}")
            print_json(response.json())
            TEST_RESULTS['用户注册'] = '通过'
            return True
        else:
            print_info(f"用户注册响应: {response.status_code}")
            print_json(response.json())
            
            # 如果用户已存在，也算测试通过
            if response.status_code == 400 and "已被注册" in response.json().get("detail", ""):
                print_info("用户已存在，跳过注册")
                TEST_RESULTS['用户注册'] = '通过'
                return True
            
            TEST_RESULTS['用户注册'] = '失败'
            return False
    except Exception as e:
        print_error(f"用户注册异常: {e}")
        TEST_RESULTS['用户注册'] = '失败'
        return False

def test_get_current_user():
    """测试获取当前用户信息"""
    print_section("获取当前用户信息")
    
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/users/me",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            print_success("获取当前用户信息成功")
            print_json(response.json())
            TEST_RESULTS['获取用户信息'] = '通过'
            return True
        else:
            print_error(f"获取当前用户信息失败: {response.status_code}")
            print_json(response.json())
            TEST_RESULTS['获取用户信息'] = '失败'
            return False
    except Exception as e:
        print_error(f"获取用户信息异常: {e}")
        TEST_RESULTS['获取用户信息'] = '失败'
        return False

#========================================
# 3. 聊天会话测试
#========================================
def test_create_session():
    """测试创建会话"""
    print_section("创建聊天会话")
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        session_data = {
            "title": f"测试会话 {timestamp}"
        }
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions/",
            json=session_data,
            headers=get_headers()
        )
        
        if response.status_code == 201:
            session = response.json()
            SESSIONS.append(session["id"])
            print_success(f"聊天会话创建成功! ID: {session['id']}")
            print_json(session)
            TEST_RESULTS['创建聊天会话'] = '通过'
            return True
        else:
            print_error(f"聊天会话创建失败: {response.status_code}")
            print_json(response.json())
            TEST_RESULTS['创建聊天会话'] = '失败'
            return False
    except Exception as e:
        print_error(f"聊天会话创建异常: {e}")
        TEST_RESULTS['创建聊天会话'] = '失败'
        return False

def test_get_sessions():
    """测试获取会话列表"""
    print_section("获取聊天会话列表")
    
    try:
        response = requests.get(
            f"{BASE_URL}{API_PREFIX}/sessions/",
            headers=get_headers()
        )
        
        if response.status_code == 200:
            sessions = response.json()
            print_success(f"获取聊天会话列表成功! 共 {len(sessions)} 个会话")
            print_json(sessions)
            TEST_RESULTS['获取会话列表'] = '通过'
            return True
        else:
            print_error(f"获取聊天会话列表失败: {response.status_code}")
            print_json(response.json())
            TEST_RESULTS['获取会话列表'] = '失败'
            return False
    except Exception as e:
        print_error(f"获取会话列表异常: {e}")
        TEST_RESULTS['获取会话列表'] = '失败'
        return False

def test_create_message():
    """测试创建消息"""
    if not SESSIONS:
        print_error("没有可用的会话ID，跳过测试")
        return False
    
    print_section("创建聊天消息")
    session_id = SESSIONS[0]
    
    try:
        # 创建用户消息
        message_data = {
            "role": "user",
            "content": f"这是一条测试消息 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}/messages",
            json=message_data,
            headers=get_headers()
        )
        
        if response.status_code == 200:
            message = response.json()
            print_success(f"创建用户消息成功! ID: {message['id']}")
            print_json(message)
            TEST_RESULTS['创建聊天消息'] = '通过'
            return True
        else:
            print_error(f"创建用户消息失败: {response.status_code}")
            print_json(response.json())
            TEST_RESULTS['创建聊天消息'] = '失败'
            return False
    except Exception as e:
        print_error(f"创建消息异常: {e}")
        TEST_RESULTS['创建聊天消息'] = '失败'
        return False

#========================================
# 4. 查询API测试
#========================================
def test_query():
    """测试查询API"""
    print_section("查询API测试")
    
    query_text = "Python中如何使用FastAPI创建Web服务?"
    
    try:
        payload = {
            "query": query_text,
            "session_id": SESSIONS[0] if SESSIONS else None
        }
        
        print_info(f"发送查询: {query_text}")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions/query",
            json=payload,
            headers=get_headers()
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"查询成功! 耗时: {elapsed:.2f}秒")
            print_info(f"会话ID: {result.get('session_id')}")
            print_info("查询结果:")
            print("-" * 60)
            print(result.get("answer", "")[:500] + "..." if len(result.get("answer", "")) > 500 else result.get("answer", ""))
            print("-" * 60)
            TEST_RESULTS['查询API'] = '通过'
            return True
        else:
            print_error(f"查询失败! 状态码: {response.status_code} (耗时: {elapsed:.2f}秒)")
            print_json(response.json())
            TEST_RESULTS['查询API'] = '失败'
            return False
    except Exception as e:
        print_error(f"查询请求异常: {e}")
        TEST_RESULTS['查询API'] = '失败'
        return False

#========================================
# 5. SSE连接测试
#========================================
async def test_sse_connection():
    """测试SSE连接是否正常工作"""
    if FastAgent is None:
        print_info("跳过SSE连接测试（未找到mcp_agent模块）")
        return True
    
    print_section("SSE连接测试")
    print_info("开始测试SSE连接...")
    
    try:
        # 导入配置信息
        from app.core.config import settings
        
        # 创建FastAgent实例，使用配置文件中的MCP服务器配置
        fast = FastAgent("TestAgent")
        
        # 定义简单的测试agent
        @fast.agent(
            name="test_assistant",
            instruction="你是一个测试助手。只需回复'SSE连接测试成功'。",
            servers=["fetch", "context7-mcp"],
            model=settings.DEFAULT_MODEL  # 使用配置文件中的默认模型
        )
        async def test_assistant_func():
            pass
        
        print_info("尝试连接SSE服务器...")
        async with fast.run() as agent:
            response = await agent.test_assistant.send("这是一个测试")
            print_success(f"SSE连接测试成功! 响应: {response}")
            TEST_RESULTS['SSE连接'] = '通过'
            return True
    except Exception as e:
        print_error(f"SSE连接测试失败: {e}")
        TEST_RESULTS['SSE连接'] = '失败'
        return False

#========================================
# 清理测试数据
#========================================
def cleanup():
    """清理测试数据"""
    print_section("清理测试数据")
    
    if not SESSIONS:
        print_info("没有需要清理的会话")
        return
    
    for session_id in SESSIONS[:]:
        try:
            response = requests.delete(
                f"{BASE_URL}{API_PREFIX}/sessions/{session_id}",
                headers=get_headers()
            )
            
            if response.status_code == 204:
                print_success(f"删除会话成功! ID: {session_id}")
                SESSIONS.remove(session_id)
            else:
                print_error(f"删除会话失败! ID: {session_id}, 状态码: {response.status_code}")
        except Exception as e:
            print_error(f"删除会话异常: {e}")

#========================================
# 测试结果汇总
#========================================
def print_test_summary():
    """打印测试总结"""
    print_header("测试结果总结")
    
    passed = 0
    failed = 0
    
    for test_name, result in TEST_RESULTS.items():
        if result == '通过':
            passed += 1
            print(f"[{Colors.GREEN}✓{Colors.END}] {test_name}")
        else:
            failed += 1
            print(f"[{Colors.RED}✗{Colors.END}] {test_name}")
    
    print("\n总结:")
    print(f"总测试数: {passed + failed}")
    print(f"通过: {Colors.GREEN}{passed}{Colors.END}")
    print(f"失败: {Colors.RED if failed > 0 else Colors.GREEN}{failed}{Colors.END}")
    
    success_rate = passed / (passed + failed) * 100 if (passed + failed) > 0 else 0
    print(f"成功率: {Colors.GREEN if success_rate >= 80 else Colors.YELLOW if success_rate >= 60 else Colors.RED}{success_rate:.1f}%{Colors.END}")

#========================================
# 主测试流程
#========================================
def run_all_tests():
    """运行所有测试"""
    print_header("FastAgent API 统一测试")
    print_info(f"开始测试 [ID: {TEST_ID}]")
    print_info(f"API基础URL: {BASE_URL}{API_PREFIX}")
    
    test_start = datetime.now()
    test_logger.info(f"[TEST:{TEST_ID}] ===== 开始API测试 [{test_start}] =====")
    
    # 1. 健康检查测试
    if not test_health():
        print_error("健康检查失败，中止测试")
        return
    
    # 2. 用户认证测试
    if not login():
        print_error("登录失败，中止测试")
        return
    
    test_register_user("testuser1", "test1@example.com", "password123")
    test_get_current_user()
    
    # 3. 聊天会话测试
    test_create_session()
    test_get_sessions()
    test_create_message()
    
    # 4. 查询API测试
    test_query()
    
    # 5. SSE连接测试
    if FastAgent:
        asyncio.run(test_sse_connection())
    
    # 清理测试数据
    cleanup()
    
    # 打印测试总结
    print_test_summary()
    
    test_end = datetime.now()
    total_time = (test_end - test_start).total_seconds()
    test_logger.info(f"[TEST:{TEST_ID}] ===== API测试完成 [{test_end}] =====")
    test_logger.info(f"[TEST:{TEST_ID}] ===== 总耗时: {total_time:.2f}秒 =====")
    print_info(f"测试完成！总耗时: {total_time:.2f}秒")

if __name__ == "__main__":
    run_all_tests() 