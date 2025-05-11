from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.services.agent_service import tech_assistant_query
from app.core.logging import app_logger

# 查询请求模型
class QueryRequest(BaseModel):
    query: str
    session_id: int = None  # 可选，如果提供则将消息保存到会话

# 查询响应模型
class QueryResponse(BaseModel):
    result: str
    session_id: int = None  # 如果是新会话，返回会话ID

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(query_data: QueryRequest):
    """处理客户端查询请求"""
    try:
        # 记录接收到的查询
        app_logger.info(f"收到查询请求: {query_data.query[:100]}...")
        
        # 调用FastAgent处理查询
        response = await tech_assistant_query(query_data.query)
        
        # 提取结果
        result = extract_answer(response)
        
        return {"result": result, "session_id": query_data.session_id}
    except Exception as e:
        app_logger.error(f"处理查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理查询失败: {str(e)}")

def extract_answer(response: str) -> str:
    """从FastAgent响应中提取最终答案"""
    if not response:
        app_logger.warning("收到空响应")
        return "无法获取回答，请稍后重试"
        
    # 查找回答的开始和结束标记
    start_marker = "$$$ANSWER_START$$$"
    end_marker = "$$$ANSWER_END$$$"
    
    start_index = response.find(start_marker)
    end_index = response.find(end_marker)
    
    if start_index != -1 and end_index != -1 and start_index < end_index:
        # 提取标记之间的内容
        answer = response[start_index + len(start_marker):end_index].strip()
        app_logger.info(f"成功提取回答，长度: {len(answer)}")
        return answer
    
    # 如果没有找到标记，记录详细内容以便调试
    app_logger.warning(f"未找到回答标记，返回完整响应。响应长度: {len(response)}")
    app_logger.debug(f"响应内容前100字符: {response[:100]}")
    app_logger.debug(f"响应内容后100字符: {response[-100:] if len(response) > 100 else response}")
    
    # 尝试查找部分标记
    if start_index != -1:
        app_logger.warning(f"找到开始标记，但未找到结束标记")
    elif end_index != -1:
        app_logger.warning(f"找到结束标记，但未找到开始标记")
    
    return response 