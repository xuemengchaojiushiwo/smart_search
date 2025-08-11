import requests
import json

def test_create_knowledge():
    """测试创建知识接口"""
    url = "http://localhost:8080/api/knowledge/create"
    
    # 测试数据1：基本数据
    data1 = {
        "name": "测试知识",
        "description": "测试描述",
        "categoryId": 1,
        "tags": "测试,标签"
    }
    
    print("测试数据1:", json.dumps(data1, ensure_ascii=False, indent=2))
    
    try:
        response = requests.post(url, json=data1, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 创建成功: {result.get('message')}")
        else:
            print(f"❌ 创建失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 测试数据2：最小数据
    data2 = {
        "name": "最小知识",
        "categoryId": 1
    }
    
    print("测试数据2:", json.dumps(data2, ensure_ascii=False, indent=2))
    
    try:
        response = requests.post(url, json=data2, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 创建成功: {result.get('message')}")
        else:
            print(f"❌ 创建失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_create_knowledge()
