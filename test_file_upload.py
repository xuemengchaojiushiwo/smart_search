#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件上传功能
验证知识创建和文档处理接口的文件上传功能
"""

import requests
import json
import os

def test_create_knowledge_with_files():
    """测试创建知识（带附件）"""
    print("📚 测试创建知识（带附件）...")
    
    # 创建测试文件
    test_files = []
    file_names = ["test1.txt", "test2.pdf", "test3.docx"]
    
    for file_name in file_names:
        file_path = f"temp_{file_name}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文件 {file_name} 的内容")
        test_files.append(('files', (file_name, open(file_path, 'rb'), 'application/octet-stream')))
    
    # 准备表单数据
    data = {
        'name': '测试知识（带附件）',
        'description': '这是一个测试知识，包含多个附件文件',
        'categoryId': '6',  # Spring Boot类目
        'tags': '测试,文件上传,附件'
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/knowledge/with-files",
            data=data,
            files=test_files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 创建知识成功: {result.get('data', {}).get('name', 'N/A')}")
            print(f"   知识ID: {result.get('data', {}).get('id', 'N/A')}")
            print(f"   附件数量: {len(test_files)}")
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

def test_process_documents():
    """测试处理多个文档"""
    print("\n📄 测试处理多个文档...")
    
    # 创建测试文件
    test_files = []
    file_names = ["document1.pdf", "document2.docx", "document3.txt"]
    
    for file_name in file_names:
        file_path = f"temp_doc_{file_name}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"这是测试文档 {file_name} 的内容")
        test_files.append(('files', (file_name, open(file_path, 'rb'), 'application/octet-stream')))
    
    try:
        response = requests.post(
            "http://localhost:8080/api/knowledge/1/documents",  # 假设知识ID为1
            files=test_files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 文档处理成功: {result.get('data', {}).get('message', 'N/A')}")
            print(f"   处理文件数: {result.get('data', {}).get('processedFiles', 'N/A')}")
        else:
            print(f"❌ 文档处理失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    finally:
        # 清理临时文件
        for file_name in file_names:
            try:
                os.remove(f"temp_doc_{file_name}")
            except:
                pass

def test_swagger_ui_file_upload():
    """测试Swagger UI中的文件上传"""
    print("\n📖 测试Swagger UI文件上传...")
    
    try:
        response = requests.get("http://localhost:8080/swagger-ui/index.html")
        if response.status_code == 200:
            print("✅ Swagger UI可访问")
            print("💡 在Swagger UI中可以测试以下接口:")
            print("   - POST /api/knowledge/with-files (创建知识带附件)")
            print("   - POST /api/knowledge/{id}/documents (处理多个文档)")
            print("   - POST /api/knowledge/{id}/document (处理单个文档)")
        else:
            print(f"❌ Swagger UI访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI异常: {e}")

def main():
    """主函数"""
    print("🚀 文件上传功能测试")
    print("=" * 50)
    
    # 测试创建知识（带附件）
    test_create_knowledge_with_files()
    
    # 测试处理多个文档
    test_process_documents()
    
    # 测试Swagger UI
    test_swagger_ui_file_upload()
    
    print("\n💡 文件上传功能说明:")
    print("- ✅ 支持多文件上传")
    print("- ✅ 文件自动保存到uploads目录")
    print("- ✅ 生成唯一文件名避免冲突")
    print("- ✅ 记录文件元数据到数据库")
    print("- ✅ 同步到Elasticsearch")
    
    print("\n🔗 可用接口:")
    print("- POST /api/knowledge/with-files (创建知识带附件)")
    print("- POST /api/knowledge/{id}/documents (处理多个文档)")
    print("- POST /api/knowledge/{id}/document (处理单个文档)")
    print("- Swagger UI: http://localhost:8080/swagger-ui/index.html")

if __name__ == "__main__":
    main() 