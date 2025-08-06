#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elasticsearch 设置和知识检索配置
"""

import requests
import json
import time
from elasticsearch import Elasticsearch

def check_es_status():
    """检查Elasticsearch状态"""
    print("🔍 检查Elasticsearch状态...")
    
    try:
        response = requests.get('http://localhost:9200/_cluster/health', timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Elasticsearch运行正常")
            print(f"   集群状态: {health.get('status')}")
            print(f"   节点数量: {health.get('number_of_nodes')}")
            print(f"   活跃分片: {health.get('active_shards')}")
            return True
        else:
            print(f"❌ Elasticsearch响应异常，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Elasticsearch，请确保已启动")
        print("💡 启动命令: cd D:\\xmc\\elasticsearch-9.1.0-windows-x86_64\\elasticsearch-9.1.0 && .\\bin\\elasticsearch.bat")
        return False
    except Exception as e:
        print(f"❌ 检查Elasticsearch失败: {e}")
        return False

def create_knowledge_index():
    """创建知识库索引"""
    print("\n📚 创建知识库索引...")
    
    try:
        es = Elasticsearch(['http://localhost:9200'])
        
        # 索引配置
        index_name = "knowledge_base"
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "long"},
                    "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "content": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "create_time": {"type": "date"},
                    "update_time": {"type": "date"},
                    "knowledge_id": {"type": "long"},
                    "chunk_id": {"type": "keyword"},
                    "chunk_content": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                    "chunk_index": {"type": "integer"},
                    "file_name": {"type": "keyword"},
                    "file_type": {"type": "keyword"},
                    "file_size": {"type": "long"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "ik_max_word": {
                            "type": "ik_max_word"
                        },
                        "ik_smart": {
                            "type": "ik_smart"
                        }
                    }
                }
            }
        }
        
        # 检查索引是否存在
        if es.indices.exists(index=index_name):
            print(f"✅ 索引 {index_name} 已存在")
            return True
        
        # 创建索引
        response = es.indices.create(index=index_name, body=mapping)
        if response.get('acknowledged'):
            print(f"✅ 索引 {index_name} 创建成功")
            return True
        else:
            print(f"❌ 索引创建失败")
            return False
            
    except Exception as e:
        print(f"❌ 创建索引失败: {e}")
        return False

def add_sample_data():
    """添加示例数据"""
    print("\n📝 添加示例数据...")
    
    try:
        es = Elasticsearch(['http://localhost:9200'])
        index_name = "knowledge_base"
        
        # 示例数据
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
        
        # 批量插入数据
        for doc in sample_docs:
            response = es.index(index=index_name, body=doc)
            if response.get('result') in ['created', 'updated']:
                print(f"✅ 文档 {doc['title']} 添加成功")
            else:
                print(f"❌ 文档 {doc['title']} 添加失败")
        
        # 刷新索引
        es.indices.refresh(index=index_name)
        print("✅ 索引刷新完成")
        return True
        
    except Exception as e:
        print(f"❌ 添加示例数据失败: {e}")
        return False

def test_search():
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    try:
        es = Elasticsearch(['http://localhost:9200'])
        index_name = "knowledge_base"
        
        # 测试搜索
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
        
        response = es.search(index=index_name, body=query)
        
        if response.get('hits', {}).get('total', {}).get('value', 0) > 0:
            print("✅ 搜索功能正常")
            print(f"   找到 {response['hits']['total']['value']} 条结果")
            
            for hit in response['hits']['hits'][:3]:  # 显示前3条
                source = hit['_source']
                print(f"   - {source.get('title', 'N/A')}")
                if 'highlight' in hit:
                    highlights = hit['highlight']
                    if 'content' in highlights:
                        print(f"     高亮: {highlights['content'][0]}")
        else:
            print("❌ 搜索无结果")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 搜索测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Elasticsearch 知识检索系统设置")
    print("=" * 50)
    
    # 检查ES状态
    if not check_es_status():
        print("\n❌ Elasticsearch未启动，请先启动ES")
        print("启动命令:")
        print("cd D:\\xmc\\elasticsearch-9.1.0-windows-x86_64\\elasticsearch-9.1.0")
        print(".\\bin\\elasticsearch.bat")
        return
    
    # 创建索引
    if not create_knowledge_index():
        print("❌ 索引创建失败")
        return
    
    # 添加示例数据
    if not add_sample_data():
        print("❌ 示例数据添加失败")
        return
    
    # 测试搜索
    if not test_search():
        print("❌ 搜索功能测试失败")
        return
    
    print("\n" + "=" * 50)
    print("✅ Elasticsearch知识检索系统设置完成！")
    print("\n💡 使用说明:")
    print("1. 索引名称: knowledge_base")
    print("2. 搜索API: POST http://localhost:9200/knowledge_base/_search")
    print("3. 管理界面: http://localhost:9200/_cat/indices?v")
    print("4. 集群健康: http://localhost:9200/_cluster/health")

if __name__ == "__main__":
    main() 