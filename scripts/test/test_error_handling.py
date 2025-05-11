#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试FastAgent错误处理的脚本
"""

import asyncio
import time
import sys
import os
import signal

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

from app.services.agent_service import get_agent_instance, close_agent_instance
from app.core.logging import app_logger

async def test_graceful_shutdown():
    """测试优雅关闭功能"""
    print("=" * 60)
    print("测试FastAgent优雅关闭")
    print("=" * 60)
    
    print("\n1. 初始化FastAgent实例")
    start_time = time.time()
    agent = await get_agent_instance()
    print(f"   初始化完成，耗时: {time.time() - start_time:.2f}秒")
    
    print("\n2. 发送测试消息")
    print("   向tech_assistant发送消息...")
    response = await agent.tech_assistant.send("你好")
    print(f"   收到回复: {response[:100]}..." if response else "无响应")
    
    print("\n3. 模拟中断信号，测试优雅关闭")
    print("   开始关闭FastAgent实例...")
    shutdown_start = time.time()
    await close_agent_instance()
    print(f"   关闭完成，耗时: {time.time() - shutdown_start:.2f}秒")
    
    print("\n4. 再次初始化并关闭，测试重复初始化和关闭")
    start_time = time.time()
    agent = await get_agent_instance()
    print(f"   重新初始化完成，耗时: {time.time() - start_time:.2f}秒")
    
    print("   再次关闭FastAgent实例...")
    shutdown_start = time.time()
    await close_agent_instance()
    print(f"   关闭完成，耗时: {time.time() - shutdown_start:.2f}秒")
    
    print("\n测试完成!")

async def test_concurrent_requests():
    """测试并发请求处理"""
    print("=" * 60)
    print("测试FastAgent并发请求处理")
    print("=" * 60)
    
    # 初始化FastAgent
    agent = await get_agent_instance()
    
    async def send_request(req_id, message):
        """发送请求并记录时间"""
        start = time.time()
        try:
            response = await agent.tech_assistant.send(message)
            print(f"请求 {req_id} 完成，耗时: {time.time() - start:.2f}秒")
            return response
        except Exception as e:
            print(f"请求 {req_id} 出错: {str(e)}")
            return None
    
    # 创建5个并发请求
    tasks = []
    for i in range(5):
        task = asyncio.create_task(
            send_request(i+1, f"简单介绍一下Python的第{i+1}个特性")
        )
        tasks.append(task)
    
    # 等待所有请求完成
    responses = await asyncio.gather(*tasks)
    
    # 关闭FastAgent
    await close_agent_instance()
    
    print("\n测试完成!")

async def main():
    """主函数"""
    await test_graceful_shutdown()
    print("\n")
    await test_concurrent_requests()

if __name__ == "__main__":
    asyncio.run(main()) 