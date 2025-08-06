#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复IK分词器问题
"""

import requests
import json

def check_es_status():
    """检查ES状态"""
    print("🔍 检查ES状态...")
    
    try:
        response = requests.get('http://localhost:9200', timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ ES运行正常")
            print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
            return True
        else:
            print(f"❌ ES响应异常: {response.status_code}")
            return False
    except:
        print("❌ ES未运行或无法连接")
        return False

def delete_knowledge_index():
    """删除知识库索引"""
    print("\n🗑️  删除现有索引...")
    
    try:
        response = requests.delete('http://localhost:9200/knowledge_base', timeout=10)
        if response.status_code == 200:
            print("✅ 索引删除成功")
            return True
        elif response.status_code == 404:
            print("ℹ️  索引不存在")
            return True
        else:
            print(f"❌ 删除索引失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 删除索引异常: {e}")
        return False

def create_index_without_ik():
    """创建不使用IK分词器的索引"""
    print("\n📚 创建知识库索引（使用标准分词器）...")
    
    # 使用标准分词器的映射
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "long"},
                "title": {"type": "text", "analyzer": "standard", "search_analyzer": "standard"},
                "content": {"type": "text", "analyzer": "standard", "search_analyzer": "standard"},
                "category": {"type": "keyword"},
                "tags": {"type": "keyword"},
                "author": {"type": "keyword"},
                "create_time": {"type": "date"},
                "update_time": {"type": "date"},
                "knowledge_id": {"type": "long"},
                "chunk_id": {"type": "keyword"},
                "chunk_content": {"type": "text", "analyzer": "standard", "search_analyzer": "standard"},
                "chunk_index": {"type": "integer"},
                "file_name": {"type": "keyword"},
                "file_type": {"type": "keyword"},
                "file_size": {"type": "long"}
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    try:
        response = requests.put(
            'http://localhost:9200/knowledge_base',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(mapping),
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ 索引创建成功")
            return True
        else:
            print(f"❌ 索引创建失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 创建索引异常: {e}")
        return False

def add_sample_data():
    """添加示例数据"""
    print("\n📝 添加示例数据...")
    
    sample_docs = [
        {
            "id": 1,
            "title": "Spring Boot 入门指南",
            "content": "Spring Boot是一个基于Spring框架的快速开发框架，它简化了Spring应用的初始搭建和开发过程。",
            "category": "技术文档",
            "tags": ["Spring Boot", "Java", "框架"],
            "author": "张三",
            "create_time": "2024-01-15T10:00:00",
            "update_time": "2024-01-15T10:00:00",
            "knowledge_id": 1,
            "chunk_id": "chunk_1_1",
            "chunk_content": "Spring Boot是一个基于Spring框架的快速开发框架，它简化了Spring应用的初始搭建和开发过程。",
            "chunk_index": 1,
            "file_name": "spring_boot_guide.md",
            "file_type": "markdown",
            "file_size": 1024
        },
        {
            "id": 2,
            "title": "Elasticsearch 搜索优化",
            "content": "Elasticsearch是一个分布式搜索引擎，本文介绍如何优化搜索性能和查询效率。",
            "category": "技术文档",
            "tags": ["Elasticsearch", "搜索", "优化"],
            "author": "李四",
            "create_time": "2024-01-16T14:30:00",
            "update_time": "2024-01-16T14:30:00",
            "knowledge_id": 2,
            "chunk_id": "chunk_2_1",
            "chunk_content": "Elasticsearch是一个分布式搜索引擎，本文介绍如何优化搜索性能和查询效率。",
            "chunk_index": 1,
            "file_name": "es_optimization.md",
            "file_type": "markdown",
            "file_size": 2048
        }
    ]
    
    success_count = 0
    for doc in sample_docs:
        try:
            response = requests.post(
                'http://localhost:9200/knowledge_base/_doc',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(doc),
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✅ 文档 '{doc['title']}' 添加成功")
                success_count += 1
            else:
                print(f"❌ 文档 '{doc['title']}' 添加失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 添加文档异常: {e}")
    
    # 刷新索引
    try:
        requests.post('http://localhost:9200/knowledge_base/_refresh', timeout=10)
        print("✅ 索引刷新完成")
    except:
        print("⚠️  索引刷新失败")
    
    return success_count > 0

def test_search():
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    query = {
        "query": {
            "multi_match": {
                "query": "Spring Boot",
                "fields": ["title", "content", "chunk_content"],
                "type": "best_fields"
            }
        },
        "highlight": {
            "fields": {
                "title": {},
                "content": {},
                "chunk_content": {}
            }
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:9200/knowledge_base/_search',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(query),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            total_hits = result.get('hits', {}).get('total', {}).get('value', 0)
            
            if total_hits > 0:
                print(f"✅ 搜索功能正常，找到 {total_hits} 条结果")
                
                # 显示搜索结果
                for hit in result['hits']['hits'][:3]:
                    source = hit['_source']
                    print(f"   - {source.get('title', 'N/A')}")
                    if 'highlight' in hit:
                        highlights = hit['highlight']
                        if 'content' in highlights:
                            print(f"     高亮: {highlights['content'][0]}")
                
                return True
            else:
                print("❌ 搜索无结果")
                return False
        else:
            print(f"❌ 搜索失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 搜索异常: {e}")
        return False

def main():
    print("🚀 修复IK分词器问题")
    print("=" * 30)
    
    # 检查ES状态
    if not check_es_status():
        print("❌ ES未运行")
        return
    
    # 删除现有索引
    if not delete_knowledge_index():
        print("❌ 删除索引失败")
        return
    
    # 创建新索引
    if not create_index_without_ik():
        print("❌ 创建索引失败")
        return
    
    # 添加示例数据
    if not add_sample_data():
        print("❌ 添加示例数据失败")
        return
    
    # 测试搜索
    if not test_search():
        print("❌ 搜索功能测试失败")
        return
    
    print("\n🎉 IK分词器问题修复完成!")
    print("💡 现在可以使用标准分词器进行搜索")
    print("💡 如果需要中文分词，可以安装IK分词器插件")

if __name__ == "__main__":
    main() 