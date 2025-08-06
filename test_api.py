#!/usr/bin/env python3
"""
API测试脚本
用于测试知识库管理系统的API功能
"""

import requests
import json
import time

# 配置
JAVA_SERVICE_URL = "http://localhost:8080"
PYTHON_SERVICE_URL = "http://localhost:8000"

def test_python_service():
    """测试Python服务"""
    print("=== 测试Python服务 ===")
    
    # 测试LDAP验证
    print("\n1. 测试LDAP验证...")
    ldap_data = {
        "username": "admin",
        "password": "password"
    }
    
    try:
        response = requests.post(f"{PYTHON_SERVICE_URL}/api/ldap/validate", 
                               json=ldap_data, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"LDAP验证测试失败: {e}")
    
    # 测试RAG对话
    print("\n2. 测试RAG对话...")
    chat_data = {
        "question": "什么是Spring Boot？",
        "user_id": "admin"
    }
    
    try:
        response = requests.post(f"{PYTHON_SERVICE_URL}/api/rag/chat", 
                               json=chat_data, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"RAG对话测试失败: {e}")

def test_java_service():
    """测试Java服务"""
    print("\n=== 测试Java服务 ===")
    
    # 测试用户登录
    print("\n1. 测试用户登录...")
    login_data = {
        "username": "admin",
        "password": "password"
    }
    
    try:
        response = requests.post(f"{JAVA_SERVICE_URL}/api/auth/login", 
                               json=login_data, timeout=5)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 获取token
        if result.get("code") == 200:
            token = result["data"]["token"]
            print(f"获取到token: {token[:20]}...")
            
            # 测试智能问答
            print("\n2. 测试智能问答...")
            chat_data = {
                "question": "什么是Spring Boot？",
                "userId": "admin"
            }
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(f"{JAVA_SERVICE_URL}/api/chat/chat", 
                                   json=chat_data, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 测试文档处理（需要先创建知识）
            print("\n3. 测试文档处理...")
            # 这里需要先创建一个知识，然后上传文档
            # 暂时跳过，因为需要实际的文件
            
        else:
            print("登录失败，无法获取token")
            
    except Exception as e:
        print(f"Java服务测试失败: {e}")

def test_python_health():
    """测试Python服务健康状态"""
    print("\n=== 测试Python服务健康状态 ===")
    
    try:
        response = requests.get(f"{PYTHON_SERVICE_URL}/api/health", timeout=5)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"健康状态: {json.dumps(result, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"健康检查失败: {e}")

def main():
    """主函数"""
    print("知识库管理系统API测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 测试Python服务
    test_python_service()
    
    # 测试Python服务健康状态
    test_python_health()
    
    # 测试Java服务
    test_java_service()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 