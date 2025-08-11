import requests
import json

def test_minimal():
    """最简单的测试，只包含必需字段"""
    url = "http://localhost:8080/api/knowledge/create"
    
    # 只包含必需的字段
    data = {
        "name": "测试",
        "categoryId": 1
    }
    
    print(f"测试数据: {json.dumps(data, ensure_ascii=False)}")
    print(f"请求URL: {url}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        # 尝试解析JSON
        try:
            result = response.json()
            print(f"解析后的响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except:
            print("响应不是有效的JSON")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_minimal()
