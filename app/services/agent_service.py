import asyncio
import time
from mcp_agent.core.fastagent import FastAgent
from app.core.logging import app_logger, log_error, log_response_info
from app.core.config import settings

# 使用单例模式，在模块加载时初始化FastAgent，避免重复初始化
_fast_agent_instance = None
_agent_instance = None
_agent_context = None

async def get_agent_instance():
    """获取FastAgent实例（单例模式）"""
    global _fast_agent_instance, _agent_instance, _agent_context
    
    if _fast_agent_instance is None:
        app_logger.info(f"初始化FastAgent [模型: {settings.DEFAULT_MODEL}]")
        _fast_agent_instance = FastAgent(settings.AGENT_NAME)
        
        # 定义tech_assistant agent
        @_fast_agent_instance.agent(
            name="tech_assistant",
            instruction="""你是一个专业的技术开发助手，专注于提供清晰、简洁、针对性的技术解答。
            你的核心职责是：
            1. 深入分析用户的技术问题，理解其核心需求。
            2. 如果用户提供了URL，使用fetch工具默默获取内容作为背景知识。
            3. 使用context7-mcp工具默默查询相关的权威技术文档作为参考。
            4. 彻底消化和整合所有收集到的信息。
            5. **最终输出的唯一要求：生成一份纯净的Markdown文档。**
                - **请务必、务必、务必使用 `$$$ANSWER_START$$$` 作为你最终答案 Markdown 的开始标记。**
                - **请务必、务必、务必使用 `$$$ANSWER_END$$$` 作为你最终答案 Markdown 的结束标记。**
                - 在这两个标记之间的内容，应该是直接回答用户原始问题的、结构清晰的Markdown，只包含必要的解释、说明和代码示例。
                - **绝对禁止在这两个标记之间包含任何关于工具使用、工具原始输出、成功/失败消息或任何中间步骤的描述。**
                - 以中文回复。

            用户只想看到被 `$$$ANSWER_START$$$` 和 `$$$ANSWER_END$$$` 包裹的最终答案。
            """,
            servers=["fetch", "context7-mcp"],
            model=settings.DEFAULT_MODEL  # 使用配置文件中的默认模型设置
        )
        async def tech_assistant_func():
            # 这个函数体不会被调用，仅作为装饰器的要求
            pass
        
        # 使用异步上下文管理器预先初始化，避免每次查询都重新建立连接
        # 保存上下文管理器而不是直接获取实例，这样可以正确关闭
        _agent_context = _fast_agent_instance.run()
        _agent_instance = await _agent_context.__aenter__()
    
    return _agent_instance

# 关闭FastAgent实例
async def close_agent_instance():
    """关闭FastAgent实例，释放资源"""
    global _agent_instance, _fast_agent_instance, _agent_context
    
    if _agent_instance is not None and _agent_context is not None:
        try:
            # 正确地关闭上下文管理器
            await _agent_context.__aexit__(None, None, None)
            app_logger.info("已关闭FastAgent实例")
        except Exception as e:
            app_logger.error(f"关闭FastAgent实例时出错: {str(e)}")
        finally:
            _agent_instance = None
            _fast_agent_instance = None
            _agent_context = None

# tech_assistant调用函数
async def tech_assistant_query(query: str, timeout: float = 180.0):
    """使用tech_assistant agent处理查询"""
    try:
        start_time = time.time()
        
        # 获取预初始化的agent实例
        agent = await get_agent_instance()
        
        # 发送查询
        app_logger.info("向agent发送查询...")
        response = await asyncio.wait_for(
            agent.tech_assistant.send(query),
            timeout=timeout
        )
        
        processing_time = time.time() - start_time
        response_length = len(response) if response else 0
        log_response_info(response_length, processing_time)
        return response
    except asyncio.TimeoutError:
        log_error(f"请求处理超时 (timeout={timeout}s)")
        raise Exception("请求处理超时")
    except Exception as e:
        log_error(f"Agent查询失败: {e}", exc_info=True)
        # 返回友好错误信息，保持格式与正常回答一致
        return "$$$ANSWER_START$$$\n## 处理查询时出错\n\n很抱歉，在处理您的查询时遇到技术问题。请稍后再试。\n\n错误详情: " + str(e) + "\n$$$ANSWER_END$$$" 