#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Elasticsearch搜索修复
验证修复ClassCastException后的搜索功能
"""

import requests
import json
import os
from datetime import datetime

def test_elasticsearch_search():
    """测试Elasticsearch搜索功能"""
    print("🔍 测试Elasticsearch搜索功能...")
    
    # 测试搜索接口
    search_keywords = ["测试", "文档", "知识", "技术"]
    
    for keyword in search_keywords:
        print(f"\n📝 搜索关键词: {keyword}")
        
        try:
            # 测试搜索
            response = requests.get(
                f"http://localhost:8080/api/es/search",
                params={
                    "query": keyword,
                    "page": 1,
                    "size": 10
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 搜索成功")
                print(f"   状态码: {response.status_code}")
                
                # 检查响应结构
                print(f"   响应结构: {type(result)}")
                print(f"   响应内容: {result}")
                
                # 根据响应结构解析数据
                if isinstance(result, dict):
                    data = result.get('data', {})
                    if isinstance(data, list):
                        # 如果data是列表，直接使用
                        results = data
                        total = len(data)
                    else:
                        # 如果data是字典，尝试获取total和results
                        total = data.get('total', 0)
                        results = data.get('results', [])
                elif isinstance(result, list):
                    # 如果整个响应是列表
                    results = result
                    total = len(result)
                else:
                    results = []
                    total = 0
                
                print(f"   总结果数: {total}")
                print(f"   当前页结果数: {len(results)}")
                
                if results:
                    print("   搜索结果:")
                    for i, item in enumerate(results, 1):
                        print(f"     {i}. ID: {item.get('id')}")
                        print(f"        标题: {item.get('title', 'N/A')}")
                        print(f"        分类ID: {item.get('categoryId', 'N/A')}")
                        print(f"        作者: {item.get('author', 'N/A')}")
                        print(f"        标签: {item.get('tags', 'N/A')}")
                        print(f"        评分: {item.get('score', 'N/A')}")
                        print(f"        附件: {item.get('attachmentNames', [])}")
                        
                        # 检查高亮内容
                        if item.get('highlightTitle'):
                            print(f"        高亮标题: {item.get('highlightTitle')}")
                        if item.get('highlightContent'):
                            print(f"        高亮内容: {item.get('highlightContent')}")
                        if item.get('highlightTags'):
                            print(f"        高亮标签: {item.get('highlightTags')}")
                        print()
                else:
                    print("   ⚠️ 没有搜索结果")
            else:
                print(f"❌ 搜索失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 搜索异常: {e}")

def test_elasticsearch_status():
    """测试Elasticsearch状态"""
    print("\n🔍 测试Elasticsearch状态...")
    
    try:
        response = requests.get("http://localhost:8080/api/es/search/count", params={"query": "test"})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Elasticsearch状态检查成功")
            print(f"   状态: {result.get('data', {}).get('status', 'N/A')}")
        else:
            print(f"❌ Elasticsearch状态检查失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ Elasticsearch状态检查异常: {e}")

def test_search_with_different_queries():
    """测试不同查询条件"""
    print("\n🔍 测试不同查询条件...")
    
    test_cases = [
        {"query": "技术", "page": 1, "size": 5},
        {"query": "文档", "page": 1, "size": 3},
        {"query": "测试", "page": 1, "size": 10},
        {"query": "知识", "page": 1, "size": 2},
        {"query": "系统", "page": 1, "size": 1}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试用例 {i}: {test_case}")
        
        try:
            response = requests.get(
                "http://localhost:8080/api/es/search",
                params=test_case
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 根据响应结构解析数据
                if isinstance(result, dict):
                    data = result.get('data', {})
                    if isinstance(data, list):
                        results = data
                        total = len(data)
                    else:
                        total = data.get('total', 0)
                        results = data.get('results', [])
                elif isinstance(result, list):
                    results = result
                    total = len(result)
                else:
                    results = []
                    total = 0
                
                print(f"✅ 查询成功 - 总数: {total}, 结果数: {len(results)}")
                
                # 检查categoryId字段是否正确处理
                for result_item in results:
                    category_id = result_item.get('categoryId')
                    if category_id is not None:
                        print(f"   ✅ categoryId正确: {category_id} (类型: {type(category_id).__name__})")
                    else:
                        print(f"   ⚠️ categoryId为空")
                        
            else:
                print(f"❌ 查询失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ 查询异常: {e}")

def test_error_handling():
    """测试错误处理"""
    print("\n🔍 测试错误处理...")
    
    # 测试空查询
    try:
        response = requests.get(
            "http://localhost:8080/api/es/search",
            params={"query": "", "page": 1, "size": 10}
        )
        print(f"空查询响应: {response.status_code}")
    except Exception as e:
        print(f"空查询异常: {e}")
    
    # 测试特殊字符
    try:
        response = requests.get(
            "http://localhost:8080/api/es/search",
            params={"query": "!@#$%^&*()", "page": 1, "size": 10}
        )
        print(f"特殊字符查询响应: {response.status_code}")
    except Exception as e:
        print(f"特殊字符查询异常: {e}")

def main():
    """主函数"""
    print("🚀 开始测试Elasticsearch搜索修复...")
    print("=" * 50)
    
    # 测试基本搜索功能
    test_elasticsearch_search()
    
    # 测试Elasticsearch状态
    test_elasticsearch_status()
    
    # 测试不同查询条件
    test_search_with_different_queries()
    
    # 测试错误处理
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("✅ Elasticsearch搜索修复测试完成")

if __name__ == "__main__":
    main() 