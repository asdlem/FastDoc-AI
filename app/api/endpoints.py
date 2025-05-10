import time
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from app.core.logging import api_logger
from app.services.agent_service import tech_assistant_query
from app.utils.text_utils import extract_urls

# 创建API路由器
router = APIRouter()

# 请求模型
class QueryRequest(BaseModel):
    query: str

# 健康检查端点
@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "timestamp": time.time()}

# 查询端点
@router.post("/query")
async def query_endpoint(request: QueryRequest):
    """API端点，接收POST请求并直接返回Markdown响应"""
    query = request.query
    api_logger.info(f"收到查询: {query}")

    urls = extract_urls(query)
    api_logger.info(f"提取的URL: {urls}")
    
    # 构造提示词
    if urls:
        # 移除查询中的 @URL 部分
        cleaned_query = query
        for url_pattern in [r'@(https?://\S+)', r'(https?://[^\s\'"\)]+)']:
            from app.utils.text_utils import clean_query
            cleaned_query = clean_query(query, url_pattern)

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
    api_logger.info(f"构造的提示词: {prompt}")

    try:
        # 设置重试逻辑
        max_retries = 2
        retry_delay = 3  # 秒
        
        result_raw = None
        for attempt in range(max_retries):
            try:
                # 调用agent服务
                result_raw = await tech_assistant_query(prompt)
                api_logger.info(f"Agent响应(原始，前500字符): {result_raw[:500]}...") 
                break  # 如果成功，跳出循环
            except Exception as e:
                if attempt < max_retries - 1:
                    api_logger.warning(f"处理请求失败 (尝试 {attempt+1}/{max_retries}): {e}，等待{retry_delay}秒后重试...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise  # 最后一次尝试失败时抛出异常
        
        # 基于特殊标记提取最终答案
        from app.utils.text_utils import extract_marked_content
        final_answer_content = extract_marked_content(result_raw)
        
        # 直接返回Markdown内容，不包装在JSON中
        return Response(content=final_answer_content, media_type="text/markdown")
    except Exception as e:
        api_logger.error(f"处理请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}") 