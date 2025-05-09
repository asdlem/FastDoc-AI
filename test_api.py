import requests
import json

api_url = "http://localhost:5000/query"

query_data = {
    "query": "帮我查一下RocketMQ快速开发的文档"
}

headers = {
    'Content-Type': 'application/json'
}

try:
    # 发送POST请求
    response = requests.post(api_url, headers=headers, json=query_data)
    response.raise_for_status()  # 如果状态码不是200，则抛出异常

    print(f"请求成功，状态码: {response.status_code}")
    print(f"响应内容类型: {response.headers.get('Content-Type')}")
    print("API响应 (Markdown):")

    # 直接获取文本内容
    response_text = response.text
    
    # 打印Markdown文本
    print(response_text)

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
    if hasattr(e, 'response') and e.response is not None:
        try:
            print("错误响应内容:")
            print(e.response.json())
        except json.JSONDecodeError:
            print(e.response.text)
except json.JSONDecodeError:
    print("无法解析返回的JSON响应")
    print("原始响应内容:")
    print(response.text)
except Exception as e:
    print(f"处理响应时发生错误: {e}") 