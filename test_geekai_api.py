#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

# 极客智坊API配置
GEEKAI_API_KEY = "sk-fN48cWer80XHieChQuQqGGZNdcSivSn3b9EgpH5eu6MP4eST"
GEEKAI_API_BASE = "https://geekai.co/api/v1"
GEEKAI_CHAT_URL = f"{GEEKAI_API_BASE}/chat/completions"

def test_direct_api():
    """直接测试极客智坊API"""
    print("=== 直接测试极客智坊API ===")
    
    headers = {
        "Authorization": f"Bearer {GEEKAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": "你好，请简单介绍一下你自己"
            }
        ],
        "temperature": 0.7
    }
    
    try:
        print("发送请求到极客智坊API...")
        response = requests.post(
            GEEKAI_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API调用成功!")
            print(f"模型: {result.get('model', 'unknown')}")
            print(f"回答: {result['choices'][0]['message']['content']}")
        else:
            print(f"API调用失败: {response.text}")
            
    except Exception as e:
        print(f"API调用异常: {e}")

def test_python_service():
    """测试Python服务"""
    print("\n=== 测试Python服务 ===")
    
    base_url = "http://localhost:5000"
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health")
        print(f"健康检查: {response.json()}")
    except Exception as e:
        print(f"健康检查失败: {e}")
        return
    
    # 测试简单聊天
    try:
        chat_data = {
            "message": "你好，请简单介绍一下你自己",
            "model": "gpt-4o-mini"
        }
        
        response = requests.post(
            f"{base_url}/chat",
            json=chat_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("简单聊天测试成功!")
            print(f"回答: {result['answer']}")
        else:
            print(f"简单聊天测试失败: {response.text}")
            
    except Exception as e:
        print(f"简单聊天测试异常: {e}")
    
    # 测试RAG对话
    try:
        rag_data = {
            "question": "什么是Spring Boot？",
            "context": [
                "Spring Boot是一个基于Spring框架的快速开发框架",
                "它简化了Spring应用的配置和部署过程",
                "Spring Boot提供了自动配置、起步依赖等特性"
            ],
            "model": "gpt-4o-mini"
        }
        
        response = requests.post(
            f"{base_url}/rag",
            json=rag_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("RAG对话测试成功!")
            print(f"回答: {result['answer']}")
            print(f"引用文档数: {len(result['references'])}")
        else:
            print(f"RAG对话测试失败: {response.text}")
            
    except Exception as e:
        print(f"RAG对话测试异常: {e}")

def test_stream_chat():
    """测试流式聊天"""
    print("\n=== 测试流式聊天 ===")
    
    base_url = "http://localhost:5000"
    
    try:
        chat_data = {
            "message": "请详细介绍一下Java编程语言的特点",
            "model": "gpt-4o-mini"
        }
        
        response = requests.post(
            f"{base_url}/chat/stream",
            json=chat_data,
            stream=True,
            timeout=60
        )
        
        if response.status_code == 200:
            print("流式聊天开始...")
            full_content = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        try:
                            json_data = json.loads(data)
                            if 'content' in json_data:
                                content = json_data['content']
                                print(content, end='', flush=True)
                                full_content += content
                            elif 'error' in json_data:
                                print(f"\n错误: {json_data['error']}")
                                break
                            elif json_data.get('type') == 'end':
                                print("\n流式聊天结束")
                                break
                        except json.JSONDecodeError:
                            continue
        else:
            print(f"流式聊天失败: {response.text}")
            
    except Exception as e:
        print(f"流式聊天测试异常: {e}")

def test_embeddings():
    """测试向量化API"""
    print("\n=== 测试向量化API ===")
    
    base_url = "http://localhost:5000"
    
    try:
        embedding_data = {
            "texts": [
                "Spring Boot是一个快速开发框架",
                "Java是一种面向对象的编程语言",
                "Docker是一个容器化平台"
            ],
            "model": "text-embedding-ada-002"
        }
        
        response = requests.post(
            f"{base_url}/embeddings",
            json=embedding_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("向量化API测试成功!")
            print(f"向量数量: {len(result.get('data', []))}")
            for i, embedding in enumerate(result.get('data', [])):
                print(f"文本{i+1}向量维度: {len(embedding.get('embedding', []))}")
        else:
            print(f"向量化API测试失败: {response.text}")
            
    except Exception as e:
        print(f"向量化API测试异常: {e}")

if __name__ == "__main__":
    print("开始测试极客智坊API...")
    
    # 1. 直接测试API
    test_direct_api()
    
    # 2. 测试Python服务
    test_python_service()
    
    # 3. 测试流式聊天
    test_stream_chat()
    
    # 4. 测试向量化
    test_embeddings()
    
    print("\n测试完成!") 