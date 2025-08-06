#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试版本管理功能
验证文档hash检测、知识版本管理、附件版本关联等功能
"""

import requests
import json
import os
import hashlib
from datetime import datetime

def calculate_file_hash(file_path):
    """计算文件hash值"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def test_version_management():
    """测试版本管理功能"""
    print("🔄 测试版本管理功能...")
    
    # 创建测试文件
    test_files = []
    file_names = ["document_v1.txt", "document_v2.txt", "document_v3.txt"]
    
    # 创建不同版本的文件
    for i, file_name in enumerate(file_names, 1):
        file_path = f"temp_{file_name}"
        content = f"这是文档版本 {i} 的内容，修改时间: {datetime.now()}"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        test_files.append(('files', (file_name, open(file_path, 'rb'), 'text/plain')))
    
    # 准备表单数据
    data = {
        'name': '版本管理测试知识',
        'description': '这是一个测试版本管理功能的知识',
        'categoryId': '6',  # Spring Boot类目
        'tags': '版本管理,测试,文档',
        'effectiveStartTime': '2025-08-06T00:00:00',
        'effectiveEndTime': '2025-12-31T23:59:59',
        'changeReason': '创建知识并上传初始文档'
    }
    
    try:
        # 第一次创建知识
        print("\n📝 第一次创建知识...")
        response = requests.post(
            "http://localhost:8080/api/knowledge/create",
            data=data,
            files=test_files
        )
        
        if response.status_code == 200:
            result = response.json()
            knowledge_id = result.get('data', {}).get('id')
            print(f"✅ 创建知识成功: ID={knowledge_id}")
            
            # 获取知识详情
            detail_response = requests.get(f"http://localhost:8080/api/knowledge/{knowledge_id}")
            if detail_response.status_code == 200:
                detail = detail_response.json()
                print(f"   知识名称: {detail.get('data', {}).get('name')}")
                print(f"   创建时间: {detail.get('data', {}).get('createdTime')}")
            
            # 第二次上传相同文件（应该被跳过）
            print("\n📝 第二次上传相同文件...")
            response2 = requests.post(
                f"http://localhost:8080/api/knowledge/{knowledge_id}/documents",
                files=test_files
            )
            
            if response2.status_code == 200:
                result2 = response2.json()
                print(f"✅ 处理结果: {result2.get('message')}")
                print(f"   版本ID: {result2.get('versionId')}")
                print(f"   版本号: {result2.get('versionNumber')}")
                print(f"   处理文件数: {result2.get('processedFiles')}")
            
            # 第三次上传修改后的文件
            print("\n📝 第三次上传修改后的文件...")
            modified_files = []
            for i, file_name in enumerate(file_names, 1):
                file_path = f"temp_modified_{file_name}"
                content = f"这是修改后的文档版本 {i} 的内容，修改时间: {datetime.now()}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified_files.append(('files', (file_name, open(file_path, 'rb'), 'text/plain')))
            
            response3 = requests.post(
                f"http://localhost:8080/api/knowledge/{knowledge_id}/documents",
                files=modified_files
            )
            
            if response3.status_code == 200:
                result3 = response3.json()
                print(f"✅ 处理修改后的文件: {result3.get('message')}")
                print(f"   版本ID: {result3.get('versionId')}")
                print(f"   版本号: {result3.get('versionNumber')}")
                print(f"   处理文件数: {result3.get('processedFiles')}")
            
            # 清理临时文件
            for file_name in file_names:
                try:
                    os.remove(f"temp_{file_name}")
                    os.remove(f"temp_modified_{file_name}")
                except:
                    pass
                    
        else:
            print(f"❌ 创建知识失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_hash_detection():
    """测试hash检测功能"""
    print("\n🔍 测试hash检测功能...")
    
    # 创建相同内容的文件
    file1_path = "temp_same_content_1.txt"
    file2_path = "temp_same_content_2.txt"
    
    content = "这是相同内容的文件"
    
    with open(file1_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open(file2_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 计算hash值
    hash1 = calculate_file_hash(file1_path)
    hash2 = calculate_file_hash(file2_path)
    
    print(f"文件1 hash: {hash1}")
    print(f"文件2 hash: {hash2}")
    print(f"Hash相同: {hash1 == hash2}")
    
    # 清理文件
    try:
        os.remove(file1_path)
        os.remove(file2_path)
    except:
        pass

def test_swagger_ui_version_features():
    """测试Swagger UI中的版本管理功能"""
    print("\n📖 测试Swagger UI版本管理功能...")
    
    try:
        response = requests.get("http://localhost:8080/swagger-ui/index.html")
        if response.status_code == 200:
            print("✅ Swagger UI可访问")
            print("💡 版本管理功能说明:")
            print("   - 文档hash检测：相同内容的文件不会重复保存")
            print("   - 知识版本管理：每次修改都会创建新版本")
            print("   - 附件版本关联：附件与知识版本关联")
            print("   - 变更原因记录：记录每次修改的原因")
        else:
            print(f"❌ Swagger UI访问失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI异常: {e}")

def main():
    """主函数"""
    print("🚀 版本管理功能测试")
    print("=" * 50)
    
    # 测试版本管理
    test_version_management()
    
    # 测试hash检测
    test_hash_detection()
    
    # 测试Swagger UI
    test_swagger_ui_version_features()
    
    print("\n💡 版本管理功能说明:")
    print("- ✅ 文档hash检测：通过SHA-256检测文件内容是否变更")
    print("- ✅ 知识版本管理：每次修改都会创建新的知识版本")
    print("- ✅ 附件版本关联：附件与知识版本建立关联关系")
    print("- ✅ 变更原因追踪：记录每次修改的具体原因")
    print("- ✅ 自动版本号：系统自动管理版本号递增")
    print("- ✅ 重复文件跳过：相同内容的文件不会重复保存")
    
    print("\n🔗 版本管理相关接口:")
    print("- POST /api/knowledge/create (创建知识，自动创建版本)")
    print("- POST /api/knowledge/{id}/documents (上传文档，创建新版本)")
    print("- GET /api/knowledge/{id} (获取知识详情)")
    print("- Swagger UI: http://localhost:8080/swagger-ui/index.html")
    
    print("\n📝 版本管理特性:")
    print("- 文件hash检测：避免重复保存相同内容的文件")
    print("- 版本历史记录：完整记录知识的修改历史")
    print("- 附件版本关联：附件与知识版本一一对应")
    print("- 变更原因追踪：记录每次修改的具体原因")
    print("- 自动版本号：系统自动管理版本号递增")

if __name__ == "__main__":
    main() 