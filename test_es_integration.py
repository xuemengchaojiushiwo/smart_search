#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ES集成功能
"""

import requests
import json
import time

def test_es_search():
    """测试ES搜索功能"""
    print("🚀 测试ES集成功能")
    print("=" * 40)
    
    # 基础URL
    base_url = "http://localhost:8080"
    
    # 测试搜索API
    print("\n🔍 测试ES搜索API...")
    
    search_url = f"{base_url}/api/es/search"
    params = {
        "query": "Spring Boot",
        "page": 1,
        "size": 10
    }
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ES搜索API调用成功")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("code") == 200:
                data = result.get("data", [])
                print(f"   搜索结果数量: {len(data)}")
                
                for i, item in enumerate(data[:3], 1):
                    print(f"   结果{i}: {item.get('title', 'N/A')}")
                    if item.get('highlightTitle'):
                        print(f"     高亮标题: {item['highlightTitle']}")
                    if item.get('highlightContent'):
                        print(f"     高亮内容: {item['highlightContent'][:100]}...")
            else:
                print(f"❌ API返回错误: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Java应用")
        print("💡 请确保Java应用已启动: mvn spring-boot:run")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_es_count():
    """测试ES计数API"""
    print("\n📊 测试ES计数API...")
    
    base_url = "http://localhost:8080"
    count_url = f"{base_url}/api/es/search/count"
    params = {"query": "Spring Boot"}
    
    try:
        response = requests.get(count_url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ES计数API调用成功")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("code") == 200:
                count = result.get("data", 0)
                print(f"   搜索结果总数: {count}")
            else:
                print(f"❌ API返回错误: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Java应用")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_knowledge_api():
    """测试知识管理API"""
    print("\n📚 测试知识管理API...")
    
    base_url = "http://localhost:8080"
    
    # 测试获取知识列表
    list_url = f"{base_url}/api/knowledge"
    params = {"page": 1, "size": 5}
    
    try:
        response = requests.get(list_url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 知识列表API调用成功")
            print(f"   状态码: {response.status_code}")
            
            if result.get("code") == 200:
                data = result.get("data", {})
                records = data.get("records", [])
                total = data.get("total", 0)
                print(f"   知识总数: {total}")
                print(f"   当前页数量: {len(records)}")
                
                for i, item in enumerate(records[:3], 1):
                    print(f"   知识{i}: {item.get('name', 'N/A')}")
            else:
                print(f"❌ API返回错误: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Java应用")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def check_java_app_status():
    """检查Java应用状态"""
    print("\n🔍 检查Java应用状态...")
    
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Java应用运行正常")
            return True
        else:
            print(f"❌ Java应用响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Java应用未运行")
        print("💡 请启动Java应用:")
        print("   cd src")
        print("   mvn spring-boot:run")
        return False
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def main():
    print("🚀 ES集成功能测试")
    print("=" * 50)
    
    # 检查Java应用状态
    if not check_java_app_status():
        return
    
    # 等待应用完全启动
    print("\n⏳ 等待应用完全启动...")
    time.sleep(2)
    
    # 测试各项功能
    test_knowledge_api()
    test_es_search()
    test_es_count()
    
    print("\n🎉 测试完成!")
    print("💡 如果测试失败，请检查:")
    print("   1. Java应用是否正常启动")
    print("   2. ES是否正常运行")
    print("   3. 网络连接是否正常")

if __name__ == "__main__":
    main() 