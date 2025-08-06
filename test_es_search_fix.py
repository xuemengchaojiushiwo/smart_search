#!/usr/bin/env python3
"""
测试ES搜索修复
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8080"
SEARCH_URL = f"{BASE_URL}/api/search"
ES_SEARCH_URL = f"{BASE_URL}/api/es/search"

def test_search():
    """测试搜索功能"""
    print("开始测试ES搜索修复...")
    
    # 测试搜索
    search_data = {
        "query": "测试",
        "page": 1,
        "size": 10
    }
    
    try:
        response = requests.post(SEARCH_URL, json=search_data)
        print(f"搜索响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("搜索成功!")
            print(f"结果数量: {len(result.get('data', {}).get('records', []))}")
            
            # 打印前几个结果
            records = result.get('data', {}).get('records', [])
            for i, record in enumerate(records[:3]):
                print(f"结果 {i+1}:")
                print(f"  ID: {record.get('id')}")
                print(f"  标题: {record.get('title')}")
                print(f"  分类ID: {record.get('categoryId')}")
                print(f"  作者: {record.get('author')}")
                print()
        else:
            print(f"搜索失败: {response.text}")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

def test_es_search():
    """测试ES搜索"""
    print("\n测试ES直接搜索...")
    
    try:
        params = {
            "query": "测试",
            "page": 1,
            "size": 10
        }
        response = requests.get(ES_SEARCH_URL, params=params)
        print(f"ES搜索响应: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("ES搜索成功!")
            data = result.get('data', [])
            print(f"结果数量: {len(data) if data else 0}")
            
            # 打印前几个结果
            if data:
                for i, record in enumerate(data[:3]):
                    print(f"ES结果 {i+1}:")
                    print(f"  ID: {record.get('id')}")
                    print(f"  标题: {record.get('title')}")
                    print(f"  分类ID: {record.get('categoryId')}")
                    print(f"  作者: {record.get('author')}")
                    print()
            else:
                print("没有找到搜索结果")
        else:
            print(f"ES搜索失败: {response.text}")
            
    except Exception as e:
        print(f"ES搜索错误: {e}")

if __name__ == "__main__":
    print("=== ES搜索修复测试 ===")
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 测试ES直接搜索
    test_es_search()
    
    # 测试综合搜索
    test_search()
    
    print("\n测试完成!") 