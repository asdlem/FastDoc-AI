import asyncio
from mcp_agent.core.fastagent import FastAgent
from app.core.logging import app_logger
from app.core.config import settings

# 创建FastAgent实例
fast = FastAgent(settings.AGENT_NAME)

# 定义tech_assistant agent
@fast.agent(
    name="tech_assistant",
    instruction="""你是一个专业的技术开发助手，专注于提供清晰、简洁、针对性的技术解答。
    你的核心职责是：
    1. 深入分析用户的技术问题，理解其核心需求。
    2. 如果用户提供了URL，使用fetch工具默默获取内容作为背景知识。
    3. 使用context7工具默默查询相关的权威技术文档作为参考。
    4. 彻底消化和整合所有收集到的信息。
    5. **最终输出的唯一要求：生成一份纯净的Markdown文档。**
        - **请务必、务必、务必使用 `$$$ANSWER_START$$$` 作为你最终答案 Markdown 的开始标记。**
        - **请务必、务必、务必使用 `$$$ANSWER_END$$$` 作为你最终答案 Markdown 的结束标记。**
        - 在这两个标记之间的内容，应该是直接回答用户原始问题的、结构清晰的Markdown，只包含必要的解释、说明和代码示例。
        - **绝对禁止在这两个标记之间包含任何关于工具使用、工具原始输出、成功/失败消息或任何中间步骤的描述。**
        - 以中文回复。

    用户只想看到被 `$$$ANSWER_START$$$` 和 `$$$ANSWER_END$$$` 包裹的最终答案。
    """,
    servers=["fetch", "context7"],
    model=settings.DEFAULT_MODEL
)
async def tech_assistant_func():
    # 这个函数体实际上不会被调用，仅作为FastAgent装饰器的要求
    pass

# tech_assistant调用函数
async def tech_assistant_query(query: str, timeout: float = 180.0):
    """使用tech_assistant agent处理查询"""
    try:
        async with fast.run() as agent:
            # 正确的调用方式是使用agent.tech_assistant.send
            response = await asyncio.wait_for(
                agent.tech_assistant.send(query),
                timeout=timeout
            )
            return response
    except asyncio.TimeoutError:
        app_logger.error(f"处理请求超时 (timeout={timeout}s)")
        raise Exception("请求处理超时")
    except Exception as e:
        app_logger.error(f"Agent查询失败: {e}")
        raise 