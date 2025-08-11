#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试Python服务的脚本
"""

import requests
import os

def test_python_service():
    """直接测试Python服务"""
    print("🧪 直接测试Python服务")
    print("=" * 60)
    
    # 测试8000端口
    url_8000 = "http://localhost:8000/api/health"
    print(f"🔍 测试端口8000: {url_8000}")
    
    try:
        response = requests.get(url_8000, timeout=5)
        print(f"   ✅ 状态码: {response.status_code}")
        print(f"   📄 响应: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试5000端口
    url_5000 = "http://localhost:5000/api/health"
    print(f"\n🔍 测试端口5000: {url_5000}")
    
    try:
        response = requests.get(url_5000, timeout=5)
        print(f"   ✅ 状态码: {response.status_code}")
        print(f"   📄 响应: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 测试文档处理接口
    print(f"\n🔍 测试文档处理接口: {url_8000.replace('/health', '/document/process')}")
    
    # 准备测试文件
    pdf_path = "python_service/file/安联美元.pdf"
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, 'rb') as f:
                files = {"file": ("安联美元.pdf", f, "application/pdf")}
                data = {
                    "knowledge_id": 29,
                    "knowledge_name": "测试知识",
                    "description": "测试描述",
                    "tags": "测试",
                    "effective_time": "2025-01-01"
                }
                
                response = requests.post(
                    url_8000.replace('/health', '/document/process'),
                    files=files,
                    data=data,
                    timeout=30
                )
                
                print(f"   ✅ 状态码: {response.status_code}")
                print(f"   📄 响应: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    else:
        print(f"   ❌ 测试文件不存在: {pdf_path}")
    
    print("\n🎉 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_python_service()
