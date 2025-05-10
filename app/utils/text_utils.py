import re
from app.core.logging import app_logger

def extract_urls(text):
    """从文本中提取URL（特别是@开头的URL）
    
    Args:
        text: 输入文本
        
    Returns:
        list: 提取出的URL列表
    """
    at_urls = re.findall(r'@(https?://\S+)', text)
    regular_urls = re.findall(r'(?<!@)(https?://[^\s\'\"\\)]+)', text)
    return list(set(at_urls + regular_urls))

def clean_query(query, url_pattern):
    """从查询中移除URL
    
    Args:
        query: 原始查询文本
        url_pattern: URL匹配模式
        
    Returns:
        str: 清理后的查询文本
    """
    return re.sub(url_pattern, '', query).strip()

def extract_marked_content(text, start_marker="$$$ANSWER_START$$$", end_marker="$$$ANSWER_END$$$"):
    """提取标记之间的内容
    
    Args:
        text: 原始文本
        start_marker: 开始标记
        end_marker: 结束标记
        
    Returns:
        str: 提取的内容，若无法提取则返回原文本
    """
    if not text:
        return ""
        
    start_index = text.find(start_marker)
    end_index = text.find(end_marker)

    if start_index != -1 and end_index != -1 and start_index < end_index:
        extracted_content = text[start_index + len(start_marker):end_index].strip()
        app_logger.info("成功提取特殊标记之间的内容")
        return extracted_content
    else:
        app_logger.warning("未找到特殊标记，返回原始内容")
        return text 