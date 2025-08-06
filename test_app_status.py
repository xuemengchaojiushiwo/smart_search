#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试应用状态
"""

import requests
import json

def test_app_status():
    """测试应用状态"""
    print("🔍 测试应用状态...")
    
    # 测试根路径
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        print(f"根路径状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
    except Exception as e:
        print(f"根路径访问失败: {e}")
    
    # 测试Swagger UI
    try:
        response = requests.get("http://localhost:8080/swagger-ui/index.html", timeout=5)
        print(f"Swagger UI状态码: {response.status_code}")
    except Exception as e:
        print(f"Swagger UI访问失败: {e}")
    
    # 测试API文档
    try:
        response = requests.get("http://localhost:8080/v3/api-docs", timeout=5)
        print(f"API文档状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"API数量: {len(data.get('paths', {}))}")
    except Exception as e:
        print(f"API文档访问失败: {e}")
    
    # 测试ES搜索API（可能需要认证）
    try:
        response = requests.get("http://localhost:8080/api/es/search?query=test", timeout=5)
        print(f"ES搜索API状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"ES搜索响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        elif response.status_code == 403:
            print("ES搜索API需要认证")
    except Exception as e:
        print(f"ES搜索API访问失败: {e}")

if __name__ == "__main__":
    test_app_status() 