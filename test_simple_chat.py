#!/usr/bin/env python3
"""
简单的聊天测试
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8080"
CHAT_URL = f"{BASE_URL}/api/chat"

def test_simple_rag():
    """测试简单的RAG对话"""
    print("=== 测试简单RAG对话 ===")
    
    chat_data = {
        "question": "Hello, how are you?",
        "sessionId": "test-simple-001"
    }
    
    try:
        response = requests.post(f"{CHAT_URL}/rag", json=chat_data)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("RAG对话成功!")
            print(f"完整响应: {result}")
            if result.get('data'):
                print(f"回答: {result.get('data', {}).get('answer')}")
            else:
                print("响应中没有data字段")
        else:
            print(f"RAG对话失败: {response.text}")
            
    except Exception as e:
        print(f"RAG对话错误: {e}")

def test_simple_stream():
    """测试简单的流式对话"""
    print("\n=== 测试简单流式对话 ===")
    
    chat_data = {
        "question": "What is RAG?",
        "sessionId": "test-stream-002"
    }
    
    try:
        response = requests.post(f"{CHAT_URL}/stream", json=chat_data, stream=True)
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("开始接收流式数据...")
            line_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_count += 1
                    print(f"第{line_count}行: {line}")
                    
                    # 只显示前10行
                    if line_count >= 10:
                        print("... (显示前10行)")
                        break
        else:
            print(f"流式对话失败: {response.text}")
            
    except Exception as e:
        print(f"流式对话错误: {e}")

if __name__ == "__main__":
    print("=== 简单聊天测试 ===")
    
    # 测试普通RAG对话
    test_simple_rag()
    
    # 测试流式对话
    test_simple_stream()
    
    print("\n测试完成!") 