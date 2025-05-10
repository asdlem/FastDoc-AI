import asyncio
from mcp_agent.core.fastagent import FastAgent
from app.core.logging import app_logger
from app.core.config import settings

async def verify_mcp_servers():
    """测试MCP服务器连接，使用passthrough模型避免消耗token"""
    try:
        # 创建一个临时FastAgent用于测试
        test_fast = FastAgent("MCP服务器测试")
        
        # 使用passthrough模型定义测试agent
        @test_fast.agent(
            name="test_agent",
            instruction="测试MCP服务器连接",
            servers=["fetch", "context7"],
            model="passthrough"  # 不调用真实LLM的内置模型
        )
        async def test_agent_func():
            pass  # 这个函数体不会被调用，仅满足装饰器语法
            
        # 使用with语句运行agent
        async with test_fast.run() as agent:
            # 尝试获取服务器信息
            results = {}
            all_connected = True
            
            # 测试fetch服务器
            try:
                app_logger.info("测试fetch服务器连接...")
                response = await agent.test_agent.send("***FIXED_RESPONSE 连接测试")
                app_logger.info(f"fetch服务器连接成功: {response}")
                results["fetch"] = {"status": "connected"}
            except Exception as e:
                app_logger.warning(f"fetch服务器连接失败: {e}")
                results["fetch"] = {"status": "error", "error": str(e)}
                all_connected = False
                
            # 测试context7服务器
            try:
                app_logger.info("测试context7服务器连接...")
                response = await agent.test_agent.send("***FIXED_RESPONSE 连接测试")
                app_logger.info(f"context7服务器连接成功: {response}")
                results["context7"] = {"status": "connected"}
            except Exception as e:
                app_logger.warning(f"context7服务器连接失败: {e}")
                results["context7"] = {"status": "error", "error": str(e)}
                all_connected = False
                
            return all_connected
    except Exception as e:
        app_logger.error(f"MCP服务器测试过程中出错: {e}")
        return False

async def retry_verify_mcp_servers(max_attempts=3, retry_delay=5):
    """带重试机制的MCP服务器连接测试"""
    for attempt in range(max_attempts):
        try:
            all_connected = await verify_mcp_servers()
            
            if all_connected:
                app_logger.info("所有MCP服务器连接成功")
                return True
            elif attempt < max_attempts - 1:
                app_logger.warning(f"部分MCP服务器连接失败，将在{retry_delay}秒后重试 ({attempt+1}/{max_attempts})...")
                await asyncio.sleep(retry_delay)
            else:
                app_logger.warning("部分MCP服务器连接最终失败，但将继续尝试运行...")
                return False
                
        except Exception as e:
            if attempt < max_attempts - 1:
                app_logger.warning(f"MCP服务器连接测试出错，将在{retry_delay}秒后重试 ({attempt+1}/{max_attempts}): {e}")
                await asyncio.sleep(retry_delay)
            else:
                app_logger.error(f"MCP服务器连接测试最终失败: {e}")
                return False
    
    return False 