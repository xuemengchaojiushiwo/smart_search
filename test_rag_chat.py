#!/usr/bin/env python3
"""
测试RAG对话接口
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8080"
CHAT_URL = f"{BASE_URL}/api/chat"

def test_create_rag_session():
    """测试创建RAG会话"""
    print("=== 测试创建RAG会话 ===")
    
    session_data = {
        "sessionName": "技术支持会话",
        "description": "用于技术问题咨询的RAG会话",
        "knowledgeIds": [1, 2, 3]
    }
    
    try:
        response = requests.post(f"{CHAT_URL}/sessions", json=session_data)
        print(f"创建RAG会话响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("创建RAG会话成功!")
            print(f"会话ID: {result.get('data', {}).get('sessionId')}")
            print(f"会话名称: {result.get('data', {}).get('sessionName')}")
            print(f"知识库ID: {result.get('data', {}).get('knowledgeIds')}")
        else:
            print(f"创建RAG会话失败: {response.text}")
            
    except Exception as e:
        print(f"创建RAG会话错误: {e}")

def test_get_rag_sessions():
    """测试获取RAG会话列表"""
    print("\n=== 测试获取RAG会话列表 ===")
    
    try:
        response = requests.get(f"{CHAT_URL}/sessions")
        print(f"获取RAG会话列表响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            sessions = result.get('data', [])
            print(f"RAG会话数量: {len(sessions)}")
            
            for i, session in enumerate(sessions[:3]):
                print(f"RAG会话 {i+1}:")
                print(f"  ID: {session.get('sessionId')}")
                print(f"  名称: {session.get('sessionName')}")
                print(f"  知识库ID: {session.get('knowledgeIds')}")
                print()
        else:
            print(f"获取RAG会话列表失败: {response.text}")
            
    except Exception as e:
        print(f"获取RAG会话列表错误: {e}")

def test_rag_chat():
    """测试RAG对话"""
    print("\n=== 测试RAG对话 ===")
    
    chat_data = {
        "question": "请介绍一下知识库的功能和特点",
        "sessionId": "test-rag-session-001",
        "knowledgeIds": [1, 2, 3]
    }
    
    try:
        response = requests.post(f"{CHAT_URL}/rag", json=chat_data)
        print(f"RAG对话响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("RAG对话成功!")
            print(f"回答: {result.get('data', {}).get('answer')}")
            print(f"会话ID: {result.get('data', {}).get('sessionId')}")
            
            # 打印知识引用
            references = result.get('data', {}).get('references', [])
            if references:
                print(f"知识引用数量: {len(references)}")
                for i, ref in enumerate(references[:2]):
                    print(f"引用 {i+1}:")
                    print(f"  知识ID: {ref.get('knowledgeId')}")
                    print(f"  知识名称: {ref.get('knowledgeName')}")
                    print(f"  相关性: {ref.get('relevance')}")
                    print()
        else:
            print(f"RAG对话失败: {response.text}")
            
    except Exception as e:
        print(f"RAG对话错误: {e}")

def test_rag_stream_chat():
    """测试RAG流式对话"""
    print("\n=== 测试RAG流式对话 ===")
    
    chat_data = {
        "question": "请详细介绍一下系统的架构设计",
        "sessionId": "test-rag-stream-session-002",
        "knowledgeIds": [1, 2, 3],
        "stream": True
    }
    
    try:
        response = requests.post(f"{CHAT_URL}/stream", json=chat_data, stream=True)
        print(f"RAG流式对话响应: {response.status_code}")
        
        if response.status_code == 200:
            print("RAG流式对话成功!")
            # 这里应该处理SSE流式数据
            # 由于实现复杂，这里只打印状态
            print("RAG流式响应已建立")
        else:
            print(f"RAG流式对话失败: {response.text}")
            
    except Exception as e:
        print(f"RAG流式对话错误: {e}")

def test_rag_chat_without_session():
    """测试无会话的RAG对话"""
    print("\n=== 测试无会话的RAG对话 ===")
    
    chat_data = {
        "question": "什么是RAG技术？",
        "knowledgeIds": [1, 2, 3]
    }
    
    try:
        response = requests.post(f"{CHAT_URL}/rag", json=chat_data)
        print(f"无会话RAG对话响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("无会话RAG对话成功!")
            print(f"回答: {result.get('data', {}).get('answer')}")
            print(f"会话ID: {result.get('data', {}).get('sessionId')}")
        else:
            print(f"无会话RAG对话失败: {response.text}")
            
    except Exception as e:
        print(f"无会话RAG对话错误: {e}")

if __name__ == "__main__":
    print("=== RAG对话接口测试 ===")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 测试各个接口
    test_create_rag_session()
    test_get_rag_sessions()
    test_rag_chat()
    test_rag_stream_chat()
    test_rag_chat_without_session()
    
    print("\n测试完成!") 