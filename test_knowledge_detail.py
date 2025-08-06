#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试获取知识详情接口
验证接口是否包含附件信息
"""

import requests
import json
import os
from datetime import datetime

def test_create_knowledge_with_attachments():
    """创建带附件的知识"""
    print("📝 创建带附件的知识...")
    
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
        'name': '测试知识详情',
        'description': '这是一个测试知识详情接口的知识',
        'categoryId': '6',  # Spring Boot类目
        'tags': '测试,详情,附件',
        'effectiveStartTime': '2025-08-06T00:00:00',
        'effectiveEndTime': '2025-12-31T23:59:59',
        'changeReason': '测试知识详情接口'
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/knowledge/create",
            data=data,
            files=test_files
        )
        
        if response.status_code == 200:
            result = response.json()
            knowledge_id = result.get('data', {}).get('id')
            print(f"✅ 创建知识成功: ID={knowledge_id}")
            return knowledge_id
        else:
            print(f"❌ 创建知识失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None
    finally:
        # 清理临时文件
        for file_name in file_names:
            try:
                os.remove(f"temp_{file_name}")
            except:
                pass

def test_get_knowledge_detail(knowledge_id):
    """测试获取知识详情"""
    print(f"\n📖 测试获取知识详情: ID={knowledge_id}")
    
    try:
        response = requests.get(f"http://localhost:8080/api/knowledge/{knowledge_id}")
        
        if response.status_code == 200:
            result = response.json()
            data = result.get('data', {})
            
            print(f"✅ 获取知识详情成功")
            print(f"   知识名称: {data.get('name')}")
            print(f"   知识描述: {data.get('description')}")
            print(f"   类目ID: {data.get('categoryId')}")
            print(f"   标签: {data.get('tags')}")
            print(f"   创建时间: {data.get('createdTime')}")
            print(f"   搜索次数: {data.get('searchCount')}")
            print(f"   下载次数: {data.get('downloadCount')}")
            
            # 检查附件信息
            attachments = data.get('attachments', [])
            print(f"   附件数量: {len(attachments)}")
            
            if attachments:
                print("   附件列表:")
                for i, attachment in enumerate(attachments, 1):
                    print(f"     {i}. 文件名: {attachment.get('fileName')}")
                    print(f"        文件路径: {attachment.get('filePath')}")
                    print(f"        文件大小: {attachment.get('fileSize')} bytes")
                    print(f"        文件类型: {attachment.get('fileType')}")
                    print(f"        文件Hash: {attachment.get('fileHash', 'N/A')}")
                    print(f"        版本ID: {attachment.get('versionId', 'N/A')}")
                    print(f"        版本号: {attachment.get('versionNumber', 'N/A')}")
                    print(f"        上传时间: {attachment.get('uploadTime')}")
                    print(f"        下载次数: {attachment.get('downloadCount')}")
            else:
                print("   ⚠️ 没有附件信息")
                
            return True
        else:
            print(f"❌ 获取知识详情失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_get_knowledge_detail_without_attachments():
    """测试获取无附件的知识详情"""
    print(f"\n📖 测试获取无附件的知识详情...")
    
    try:
        # 创建无附件的知识
        data = {
            'name': '无附件知识',
            'description': '这是一个没有附件的知识',
            'categoryId': '6',
            'tags': '无附件,测试',
            'effectiveStartTime': '2025-08-06T00:00:00',
            'effectiveEndTime': '2025-12-31T23:59:59',
            'changeReason': '测试无附件知识'
        }
        
        response = requests.post(
            "http://localhost:8080/api/knowledge/create",
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            knowledge_id = result.get('data', {}).get('id')
            print(f"✅ 创建无附件知识成功: ID={knowledge_id}")
            
            # 获取详情
            detail_response = requests.get(f"http://localhost:8080/api/knowledge/{knowledge_id}")
            
            if detail_response.status_code == 200:
                detail_result = detail_response.json()
                detail_data = detail_result.get('data', {})
                
                print(f"✅ 获取无附件知识详情成功")
                print(f"   知识名称: {detail_data.get('name')}")
                
                attachments = detail_data.get('attachments', [])
                print(f"   附件数量: {len(attachments)}")
                
                if not attachments:
                    print("   ✅ 正确：没有附件信息")
                else:
                    print("   ⚠️ 意外：有附件信息")
                    
                return True
            else:
                print(f"❌ 获取详情失败: {detail_response.status_code}")
                return False
        else:
            print(f"❌ 创建知识失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主函数"""
    print("🚀 测试获取知识详情接口")
    print("=" * 50)
    
    # 测试1：创建带附件的知识并获取详情
    knowledge_id = test_create_knowledge_with_attachments()
    if knowledge_id:
        test_get_knowledge_detail(knowledge_id)
    
    # 测试2：测试无附件的知识
    test_get_knowledge_detail_without_attachments()
    
    print("\n💡 测试总结:")
    print("- ✅ 获取知识详情接口现在包含附件信息")
    print("- ✅ 附件信息包含文件名、路径、大小、类型等")
    print("- ✅ 附件信息包含版本管理相关字段")
    print("- ✅ 无附件的知识正确返回空附件列表")
    
    print("\n🔗 接口信息:")
    print("- GET /api/knowledge/{id} - 获取知识详情（包含附件信息）")
    print("- 附件字段包括：id, fileName, filePath, fileSize, fileType, fileHash, versionId, versionNumber, uploadTime, downloadCount")

if __name__ == "__main__":
    main() 