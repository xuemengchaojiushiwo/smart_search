import requests
import json

def test_create_knowledge_detailed():
    """详细测试创建知识接口的各种情况"""
    base_url = "http://localhost:8080/api/knowledge/create"
    
    test_cases = [
        {
            "name": "空名称测试",
            "data": {"name": "", "categoryId": 1},
            "expected": "应该返回400验证错误"
        },
        {
            "name": "缺少名称测试",
            "data": {"categoryId": 1},
            "expected": "应该返回400验证错误"
        },
        {
            "name": "缺少类目ID测试",
            "data": {"name": "测试知识"},
            "expected": "应该返回400验证错误"
        },
        {
            "name": "类目ID为null测试",
            "data": {"name": "测试知识", "categoryId": None},
            "expected": "应该返回400验证错误"
        },
        {
            "name": "正常数据测试",
            "data": {"name": "测试知识", "description": "测试描述", "categoryId": 1, "tags": "测试,标签"},
            "expected": "应该返回200成功"
        },
        {
            "name": "最小数据测试",
            "data": {"name": "最小知识", "categoryId": 1},
            "expected": "应该返回200成功"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"期望结果: {test_case['expected']}")
        print(f"测试数据: {json.dumps(test_case['data'], ensure_ascii=False, indent=2)}")
        print('-'*60)
        
        try:
            # 处理None值
            data = {k: v for k, v in test_case['data'].items() if v is not None}
            
            response = requests.post(base_url, json=data, timeout=10)
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应体: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 成功: {result.get('message', '无消息')}")
            elif response.status_code == 400:
                print(f"⚠️  验证错误: {response.text}")
            else:
                print(f"❌ 其他错误: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print('='*60)

if __name__ == "__main__":
    test_create_knowledge_detailed()
