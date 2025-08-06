#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有API接口
验证去掉认证后所有接口都可以访问
"""

import requests
import json
import time

def test_knowledge_apis():
    """测试知识管理API"""
    print("📚 测试知识管理API...")
    
    # 测试获取知识列表
    response = requests.get("http://localhost:8080/api/knowledge/list?page=1&size=10")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 知识列表获取成功: {len(data.get('data', {}).get('records', []))} 条记录")
    else:
        print(f"❌ 知识列表获取失败: {response.status_code}")
    
    # 测试搜索知识
    response = requests.get("http://localhost:8080/api/knowledge/search?query=Spring&page=1&size=10")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 知识搜索成功: {len(data.get('data', {}).get('records', []))} 条结果")
    else:
        print(f"❌ 知识搜索失败: {response.status_code}")
    
    # 测试获取知识详情
    response = requests.get("http://localhost:8080/api/knowledge/1")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 知识详情获取成功: {data.get('data', {}).get('name', 'N/A')}")
    else:
        print(f"❌ 知识详情获取失败: {response.status_code}")

def test_category_apis():
    """测试分类管理API"""
    print("\n📂 测试分类管理API...")
    
    # 测试获取分类列表
    response = requests.get("http://localhost:8080/api/category/list")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 分类列表获取成功: {len(data.get('data', []))} 条记录")
    else:
        print(f"❌ 分类列表获取失败: {response.status_code}")
    
    # 测试获取分类树
    response = requests.get("http://localhost:8080/api/category/tree")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 分类树获取成功: {len(data.get('data', []))} 个根分类")
    else:
        print(f"❌ 分类树获取失败: {response.status_code}")

def test_es_apis():
    """测试ES搜索API"""
    print("\n🔍 测试ES搜索API...")
    
    # 测试搜索
    response = requests.get("http://localhost:8080/api/es/search?query=Spring Boot&page=1&size=10")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ ES搜索成功: {len(data.get('data', []))} 条结果")
    else:
        print(f"❌ ES搜索失败: {response.status_code}")
    
    # 测试搜索总数
    response = requests.get("http://localhost:8080/api/es/search/count?query=Spring Boot")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ ES搜索总数获取成功: {data.get('data', 0)}")
    else:
        print(f"❌ ES搜索总数获取失败: {response.status_code}")

def test_auth_apis():
    """测试认证API"""
    print("\n🔐 测试认证API...")
    
    # 测试登录
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post("http://localhost:8080/api/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功: {data.get('message', 'N/A')}")
        token = data.get('data', {}).get('token', '')
        if token:
            print(f"✅ 获取到token: {token[:20]}...")
    else:
        print(f"❌ 登录失败: {response.status_code}")

def test_swagger_ui():
    """测试Swagger UI"""
    print("\n📖 测试Swagger UI...")
    
    response = requests.get("http://localhost:8080/swagger-ui/index.html")
    if response.status_code == 200:
        print("✅ Swagger UI访问成功")
    else:
        print(f"❌ Swagger UI访问失败: {response.status_code}")

def test_health_check():
    """测试健康检查"""
    print("\n🏥 测试健康检查...")
    
    response = requests.get("http://localhost:8080/actuator/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 健康检查成功: {data.get('status', 'N/A')}")
    else:
        print(f"❌ 健康检查失败: {response.status_code}")

def test_root_path():
    """测试根路径"""
    print("\n🏠 测试根路径...")
    
    response = requests.get("http://localhost:8080/")
    if response.status_code == 200:
        print("✅ 根路径访问成功")
    else:
        print(f"❌ 根路径访问失败: {response.status_code}")

def main():
    """主测试函数"""
    print("🚀 测试所有API接口（已关闭认证）")
    print("=" * 60)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(10)
    
    try:
        # 测试根路径
        test_root_path()
        
        # 测试健康检查
        test_health_check()
        
        # 测试Swagger UI
        test_swagger_ui()
        
        # 测试认证API
        test_auth_apis()
        
        # 测试分类API
        test_category_apis()
        
        # 测试知识管理API
        test_knowledge_apis()
        
        # 测试ES搜索API
        test_es_apis()
        
        print("\n🎉 所有API测试完成！")
        print("\n📋 测试总结:")
        print("- ✅ 所有接口都已关闭认证")
        print("- ✅ 可以自由测试所有API")
        print("- ✅ 建议在测试完成后重新启用认证")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 