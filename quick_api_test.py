#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速API测试
验证主要接口的访问
"""

import requests
import json

def test_main_apis():
    """测试主要API接口"""
    print("🚀 快速API测试（认证已关闭）")
    print("=" * 40)
    
    # 测试ES搜索API
    print("\n🔍 测试ES搜索API...")
    try:
        response = requests.get("http://localhost:8080/api/es/search?query=Spring Boot&page=1&size=10")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ES搜索成功: {len(data.get('data', []))} 条结果")
            for item in data.get('data', []):
                print(f"  - {item.get('title', 'N/A')} (ID: {item.get('id', 'N/A')})")
        else:
            print(f"❌ ES搜索失败: {response.status_code}")
    except Exception as e:
        print(f"❌ ES搜索异常: {e}")
    
    # 测试ES搜索总数
    print("\n📊 测试ES搜索总数...")
    try:
        response = requests.get("http://localhost:8080/api/es/search/count?query=Spring Boot")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ES搜索总数: {data.get('data', 0)}")
        else:
            print(f"❌ ES搜索总数失败: {response.status_code}")
    except Exception as e:
        print(f"❌ ES搜索总数异常: {e}")
    
    # 测试Swagger UI
    print("\n📖 测试Swagger UI...")
    try:
        response = requests.get("http://localhost:8080/swagger-ui/index.html")
        if response.status_code == 200:
            print("✅ Swagger UI访问成功")
            print("   访问地址: http://localhost:8080/swagger-ui/index.html")
        else:
            print(f"❌ Swagger UI访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI异常: {e}")
    
    # 测试健康检查
    print("\n🏥 测试健康检查...")
    try:
        response = requests.get("http://localhost:8080/actuator/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data.get('status', 'N/A')}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    print("\n🎉 测试完成！")
    print("\n📋 可用接口:")
    print("- ES搜索: GET /api/es/search?query=关键词&page=1&size=10")
    print("- ES搜索总数: GET /api/es/search/count?query=关键词")
    print("- Swagger UI: http://localhost:8080/swagger-ui/index.html")
    print("- 健康检查: GET /actuator/health")
    print("\n💡 提示: 所有接口现在都可以直接访问，无需认证")

if __name__ == "__main__":
    test_main_apis() 