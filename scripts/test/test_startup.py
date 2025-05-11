#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试FastAgent初始化性能的简单脚本
"""

import asyncio
import time
import sys
import os

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

from mcp_agent.core.fastagent import FastAgent
from app.services.agent_service import get_agent_instance, close_agent_instance

async def test_original_method():
    """测试原始方法 - 每次查询都初始化FastAgent"""
    print("测试原始方法 - 每次查询都初始化FastAgent")
    
    start_time = time.time()
    fast = FastAgent("TestAgent")
    
    # 定义agent
    @fast.agent(
        name="test_assistant",
        instruction="你是一个测试助手",
        servers=["fetch", "context7-mcp"],
        model="deepseek-chat"
    )
    async def test_agent():
        pass
    
    async with fast.run() as agent:
        print(f"FastAgent初始化完成，耗时: {time.time() - start_time:.2f}秒")
        
        # 发送测试消息
        message_start_time = time.time()
        response = await agent.test_assistant.send("你好")
        message_time = time.time() - message_start_time
        
        print(f"消息处理完成，耗时: {message_time:.2f}秒")
        print(f"回复: {response[:100]}...\n")

async def test_optimized_method():
    """测试优化方法 - 使用预初始化的FastAgent实例"""
    print("测试优化方法 - 使用预初始化的FastAgent实例")
    
    start_time = time.time()
    agent = await get_agent_instance()
    initialization_time = time.time() - start_time
    print(f"获取预初始化FastAgent实例，耗时: {initialization_time:.2f}秒")
    
    # 发送测试消息
    message_start_time = time.time()
    response = await agent.tech_assistant.send("你好")
    message_time = time.time() - message_start_time
    
    print(f"消息处理完成，耗时: {message_time:.2f}秒")
    print(f"回复: {response[:100]}...\n")
    
    # 关闭实例
    await close_agent_instance()

async def main():
    """主函数"""
    print("=" * 60)
    print("FastAgent启动性能测试")
    print("=" * 60)
    
    # 仅测试优化后的方法
    await test_optimized_method()
    
    print("测试完成!")

if __name__ == "__main__":
    asyncio.run(main()) 