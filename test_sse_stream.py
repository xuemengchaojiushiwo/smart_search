#!/usr/bin/env python3
"""
测试SSE流式响应
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8080"
CHAT_URL = f"{BASE_URL}/api/chat"

def test_sse_stream():
    """测试SSE流式响应"""
    print("=== 测试SSE流式响应 ===")
    
    chat_data = {
        "question": "请详细介绍一下RAG技术的工作原理",
        "sessionId": "test-sse-session-001",
        "knowledgeIds": [1, 2, 3],
        "stream": True
    }
    
    try:
        # 发送POST请求，设置stream=True来接收流式数据
        response = requests.post(
            f"{CHAT_URL}/stream", 
            json=chat_data, 
            stream=True,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"SSE流式响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("SSE流式响应开始...")
            print("=" * 50)
            
            # 逐行读取SSE数据
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    print(f"收到数据: {line}")
                    
                    # 解析SSE格式
                    if isinstance(line, str) and line.startswith('event:'):
                        event_type = line[6:].strip()
                        print(f"事件类型: {event_type}")
                    elif isinstance(line, str) and line.startswith('data:'):
                        data = line[5:].strip()
                        print(f"数据内容: {data}")
                        
                        # 尝试解析JSON数据
                        try:
                            json_data = json.loads(data)
                            print(f"解析的JSON: {json_data}")
                        except json.JSONDecodeError:
                            print("非JSON格式数据")
                    
                    print("-" * 30)
                    
        else:
            print(f"SSE流式响应失败: {response.text}")
            
    except Exception as e:
        print(f"SSE流式响应错误: {e}")

def test_sse_with_event_source():
    """使用EventSource模拟浏览器行为"""
    print("\n=== 模拟浏览器EventSource ===")
    
    chat_data = {
        "question": "什么是知识库？",
        "sessionId": "test-browser-session-002",
        "knowledgeIds": [1, 2, 3],
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{CHAT_URL}/stream", 
            json=chat_data, 
            stream=True,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache'
            }
        )
        
        print(f"浏览器模拟响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("开始接收SSE数据流...")
            
            # 模拟EventSource的事件处理
            events = {
                'start': [],
                'message': [],
                'references': [],
                'end': [],
                'error': []
            }
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith('event:'):
                        current_event = line[6:].strip()
                    elif line.startswith('data:'):
                        data = line[5:].strip()
                        if current_event in events:
                            events[current_event].append(data)
                            print(f"[{current_event}] {data}")
                            
                            # 处理不同类型的事件
                            if current_event == 'start':
                                print("对话开始...")
                            elif current_event == 'message':
                                print("收到消息片段...")
                            elif current_event == 'references':
                                print("收到知识引用...")
                            elif current_event == 'end':
                                print("对话结束...")
                            elif current_event == 'error':
                                print("发生错误...")
                    
        else:
            print(f"浏览器模拟失败: {response.text}")
            
    except Exception as e:
        print(f"浏览器模拟错误: {e}")

def test_simple_sse():
    """简单的SSE测试"""
    print("\n=== 简单SSE测试 ===")
    
    chat_data = {
        "question": "你好",
        "sessionId": "simple-test-003"
    }
    
    try:
        response = requests.post(
            f"{CHAT_URL}/stream", 
            json=chat_data, 
            stream=True
        )
        
        print(f"简单SSE测试状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("开始接收数据...")
            line_count = 0
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    line_count += 1
                    print(f"第{line_count}行: {line}")
                    
                    # 只显示前20行
                    if line_count >= 20:
                        print("... (显示前20行)")
                        break
        else:
            print(f"简单SSE测试失败: {response.text}")
            
    except Exception as e:
        print(f"简单SSE测试错误: {e}")

if __name__ == "__main__":
    print("=== SSE流式响应测试 ===")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 测试各种SSE场景
    test_sse_stream()
    test_sse_with_event_source()
    test_simple_sse()
    
    print("\n测试完成!") 