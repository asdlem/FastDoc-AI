import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查端点"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"健康检查响应: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_query(query_text):
    """测试查询端点"""
    try:
        payload = {"query": query_text}
        headers = {"Content-Type": "application/json"}
        
        print(f"发送查询: {query_text}")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/query", 
            data=json.dumps(payload),
            headers=headers
        )
        
        elapsed = time.time() - start_time
        
        print(f"查询响应状态码: {response.status_code} (耗时: {elapsed:.2f}秒)")
        
        if response.status_code == 200:
            result = response.json().get("result", "")
            print("\n" + "-" * 50 + "\n结果:\n" + "-" * 50)
            print(result)
            print("-" * 50)
            return True
        else:
            print(f"查询失败: {response.text}")
            return False
    except Exception as e:
        print(f"查询请求失败: {e}")
        return False

if __name__ == "__main__":
    # 先测试健康检查
    if test_health():
        print("健康检查成功，开始测试查询...")
        
        # 测试简单查询
        test_query("Python中如何使用FastAPI创建Web服务?")
        
        # 可以添加更多测试用例
    else:
        print("健康检查失败，服务可能未启动。") 