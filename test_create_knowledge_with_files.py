#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的创建知识接口
验证支持文件上传的创建知识功能
"""

import requests
import json
import os
from datetime import datetime

def test_create_knowledge_with_files():
    """测试创建知识（支持文件上传）"""
    print("📚 测试创建知识（支持文件上传）...")
    
    # 创建测试文件
    test_files = []
    file_names = ["document1.pdf", "document2.docx", "document3.txt"]
    
    for file_name in file_names:
        file_path = f"temp_{file_name}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文档 {file_name} 的内容")
        test_files.append(('files', (file_name, open(file_path, 'rb'), 'application/octet-stream')))
    
    # 准备表单数据
    data = {
        'name': 'Spring Boot 实战指南',
        'description': '这是一个关于Spring Boot的实战指南，包含详细的开发教程和最佳实践。',
        'categoryId': '6',  # Spring Boot类目
        'tags': 'Spring Boot,Java,框架,实战',
        'effectiveStartTime': '2025-08-06T00:00:00',
        'effectiveEndTime': '2025-12-31T23:59:59',
        'changeReason': '新增Spring Boot实战指南'
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/knowledge/create",
            data=data,
            files=test_files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 创建知识成功: {result.get('data', {}).get('name', 'N/A')}")
            print(f"   知识ID: {result.get('data', {}).get('id', 'N/A')}")
            print(f"   类目ID: {result.get('data', {}).get('categoryId', 'N/A')}")
            print(f"   标签: {result.get('data', {}).get('tags', 'N/A')}")
            print(f"   附件数量: {len(test_files)}")
            print(f"   创建时间: {result.get('data', {}).get('createdTime', 'N/A')}")
        else:
            print(f"❌ 创建知识失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    finally:
        # 清理临时文件
        for file_name in file_names:
            try:
                os.remove(f"temp_{file_name}")
            except:
                pass

def test_create_knowledge_without_files():
    """测试创建知识（无附件）"""
    print("\n📚 测试创建知识（无附件）...")
    
    # 准备表单数据
    data = {
        'name': 'Elasticsearch 搜索优化',
        'description': '关于Elasticsearch搜索性能优化的详细指南。',
        'categoryId': '7',  # Elasticsearch类目
        'tags': 'Elasticsearch,搜索,优化,性能',
        'effectiveStartTime': '2025-08-06T00:00:00',
        'effectiveEndTime': '2025-12-31T23:59:59',
        'changeReason': '新增Elasticsearch优化指南'
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/knowledge/create",
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 创建知识成功: {result.get('data', {}).get('name', 'N/A')}")
            print(f"   知识ID: {result.get('data', {}).get('id', 'N/A')}")
            print(f"   类目ID: {result.get('data', {}).get('categoryId', 'N/A')}")
            print(f"   标签: {result.get('data', {}).get('tags', 'N/A')}")
            print(f"   附件数量: 0")
        else:
            print(f"❌ 创建知识失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_swagger_ui_new_interface():
    """测试Swagger UI中的新接口"""
    print("\n📖 测试Swagger UI新接口...")
    
    try:
        response = requests.get("http://localhost:8080/swagger-ui/index.html")
        if response.status_code == 200:
            print("✅ Swagger UI可访问")
            print("💡 在Swagger UI中可以测试以下接口:")
            print("   - POST /api/knowledge/create (创建知识，支持文件上传)")
            print("   - POST /api/knowledge/{id}/documents (处理多个文档)")
            print("   - POST /api/knowledge/{id}/document (处理单个文档)")
        else:
            print(f"❌ Swagger UI访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI异常: {e}")

def main():
    """主函数"""
    print("🚀 新的创建知识接口测试")
    print("=" * 50)
    
    # 测试创建知识（带附件）
    test_create_knowledge_with_files()
    
    # 测试创建知识（无附件）
    test_create_knowledge_without_files()
    
    # 测试Swagger UI
    test_swagger_ui_new_interface()
    
    print("\n💡 新接口功能说明:")
    print("- ✅ 支持完整的知识信息输入")
    print("- ✅ 支持文件上传")
    print("- ✅ 支持时间字段")
    print("- ✅ 支持标签管理")
    print("- ✅ 支持变更原因记录")
    
    print("\n🔗 可用接口:")
    print("- POST /api/knowledge (创建知识，JSON格式)")
    print("- POST /api/knowledge/create (创建知识，支持文件上传)")
    print("- POST /api/knowledge/{id}/documents (处理多个文档)")
    print("- POST /api/knowledge/{id}/document (处理单个文档)")
    print("- Swagger UI: http://localhost:8080/swagger-ui/index.html")
    
    print("\n📝 接口参数说明:")
    print("- name: 知识名称（必填）")
    print("- description: 知识描述（可选）")
    print("- categoryId: 类目ID（必填）")
    print("- tags: 标签（逗号分隔，可选）")
    print("- effectiveStartTime: 生效开始时间（可选）")
    print("- effectiveEndTime: 生效结束时间（可选）")
    print("- changeReason: 变更原因（可选）")
    print("- files: 附件文件列表（可选）")

if __name__ == "__main__":
    main() 