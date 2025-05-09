import asyncio
import os
import re
import sys
import logging
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcp_agent.core.fastagent import FastAgent

# 配置日志
app_logger = logging.getLogger("FastAgentApp")
if not app_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    app_logger.addHandler(handler)
app_logger.setLevel(logging.INFO)

# 禁用其他可能有问题的logger
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# 创建FastAPI应用
app = FastAPI(title="FastAgent API")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 创建FastAgent实例
try:
    fast_agent_instance = FastAgent("技术开发助手API")
except Exception as e:
    app_logger.critical(f"初始化FastAgent失败: {e}", exc_info=True)
    sys.exit("严重错误: FastAgent初始化失败。")

@fast_agent_instance.agent(
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
    servers=["fetch", "context7"]
)
async def tech_assistant_agent_async(query: str):
    """异步函数，实际调用agent"""
    async with fast_agent_instance.run() as agent:
        result = await agent.tech_assistant(query)
        return result

def extract_urls(text):
    """从文本中提取URL（特别是@开头的URL）"""
    at_urls = re.findall(r'@(https?://\S+)', text)
    regular_urls = re.findall(r'(?<!@)(https?://[^\s\'\"\\)]+)', text)
    return list(set(at_urls + regular_urls))

# 定义请求模型
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """API端点，接收POST请求并返回Markdown响应"""
    query = request.query
    app_logger.info(f"收到查询: {query}")

    urls = extract_urls(query)
    app_logger.info(f"提取的URL: {urls}")
    
    if urls:
        # 移除查询中的 @URL 部分
        cleaned_query = query
        for url_pattern in [r'@(https?://\S+)', r'(https?://[^\s\'"\)]+)']:
            cleaned_query = re.sub(url_pattern, '', cleaned_query).strip()

        prompt = f"""请严格按照以下要求，为用户提供纯净的Markdown格式技术解答：
用户原始问题: "{cleaned_query}"
参考URL（你需要在后台处理这些URL）: {', '.join(urls)}

你的任务是：
1. 理解问题和分析URL内容。
2. 结合context7工具查找相关文档。
3. **核心：整合信息，生成最终答案。请将最终的、纯净的Markdown答案严格包裹在 `$$$ANSWER_START$$$` 和 `$$$ANSWER_END$$$` 标记之间。这两个标记之外不要有任何其他内容是给用户的。**
"""
    else:
        prompt = f"""请严格按照以下要求，为用户提供纯净的Markdown格式技术解答：
用户原始问题: "{query}"

你的任务是：
1. 理解问题。
2. 结合context7工具查找相关文档。
3. (可选，后台进行) 使用fetch补充搜索。
4. **核心：整合信息，生成最终答案。请将最终的、纯净的Markdown答案严格包裹在 `$$$ANSWER_START$$$` 和 `$$$ANSWER_END$$$` 标记之间。这两个标记之外不要有任何其他内容是给用户的。**
"""
    app_logger.info(f"构造的提示词: {prompt}")

    try:
        # 直接调用异步函数，FastAPI自动处理异步上下文
        result_raw = await tech_assistant_agent_async(prompt)
        app_logger.info(f"Agent响应(原始，前500字符): {result_raw[:500]}...") 

        # 基于特殊标记提取最终答案
        final_answer_content = ""
        start_marker = "$$$ANSWER_START$$$"
        end_marker = "$$$ANSWER_END$$$"
        start_index = result_raw.find(start_marker)
        end_index = result_raw.find(end_marker)

        if start_index != -1 and end_index != -1 and start_index < end_index:
            final_answer_content = result_raw[start_index + len(start_marker):end_index].strip()
            app_logger.info("成功提取特殊标记之间的内容。")
        else:
            app_logger.warning("未找到特殊标记。尝试备用清理逻辑。")
            # 回退清理逻辑
            temp_cleaned_result = result_raw
            if temp_cleaned_result.startswith("```markdown"): 
                first_newline_idx = temp_cleaned_result.find('\n')
                if first_newline_idx != -1: temp_cleaned_result = temp_cleaned_result[first_newline_idx+1:]
            elif temp_cleaned_result.startswith("```"): 
                first_newline_idx = temp_cleaned_result.find('\n')
                if first_newline_idx != -1: temp_cleaned_result = temp_cleaned_result[first_newline_idx+1:]
            if temp_cleaned_result.endswith("\n```"): temp_cleaned_result = temp_cleaned_result[:-len("\n```")]
            elif temp_cleaned_result.endswith("```"): temp_cleaned_result = temp_cleaned_result[:-3]
            temp_cleaned_result = temp_cleaned_result.strip()
            
            match = re.search(r"^(#{1,2}\s+.+)", temp_cleaned_result, re.MULTILINE)
            if match:
                start_index_fallback = match.start()
                final_answer_content = temp_cleaned_result[start_index_fallback:]
                app_logger.info("备用方案：提取从H1/H2标题开始的内容。")
            else:
                final_answer_content = temp_cleaned_result
                app_logger.warning("备用方案：未找到H1/H2标题。返回基本清理后的内容。")

        app_logger.info(f"最终响应(前200字符): {final_answer_content[:200]}...")
        return Response(content=final_answer_content, media_type="text/markdown; charset=utf-8")
    except Exception as e:
        app_logger.error(f"处理请求时出错: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"发生意外错误: {str(e)}")

if __name__ == '__main__':
    # 使用Uvicorn服务器运行FastAPI应用
    app_logger.info("启动Uvicorn服务器，监听http://0.0.0.0:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)