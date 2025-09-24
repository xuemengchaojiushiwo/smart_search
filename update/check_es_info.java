#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查单个Elasticsearch环境的配置和索引结构
"""

from elasticsearch import Elasticsearch
import json
import sys
import argparse
import pprint

def check_es_environment(host, port, username=None, password=None, index_name="knowledge_base_new"):
    """检查单个ES环境的信息"""
    print(f"\n===== 检查 {host}:{port} 的ES环境 =====")
    
    # 连接ES
    try:
        if username and password:
            es = Elasticsearch(
                [f"http://{host}:{port}"],
                basic_auth=(username, password)
            )
        else:
            es = Elasticsearch([f"http://{host}:{port}"])
        
        # 检查连接
        if not es.ping():
            print(f"❌ 无法连接到 {host}:{port}")
            return
            
        print(f"✅ 成功连接到 {host}:{port}")
        
        # 获取基本信息
        info = es.info()
        print("\n📌 ES版本信息:")
        print(f"版本号: {info['version']['number']}")
        print(f"构建类型: {info['version']['build_type']}")
        print(f"构建日期: {info['version'].get('build_date', 'N/A')}")
        print(f"Lucene版本: {info['version']['lucene_version']}")
        
        # 检查索引是否存在
        if not es.indices.exists(index=index_name):
            print(f"\n❌ 索引 {index_name} 不存在")
            return
        
        print(f"\n✅ 索引 {index_name} 存在")
        
        # 获取索引映射
        mapping = es.indices.get_mapping(index=index_name)
        
        # 获取索引设置
        settings = es.indices.get_settings(index=index_name)
        
        # 获取索引统计信息
        stats = es.indices.stats(index=index_name)
        
        # 检查文档数量
        doc_count = stats["_all"]["primaries"]["docs"]["count"]
        print(f"\n📊 索引中有 {doc_count} 个文档")
        
        # 检查向量维度
        print("\n📌 向量字段信息:")
        if "embedding" in mapping[index_name]["mappings"]["properties"]:
            embedding_field = mapping[index_name]["mappings"]["properties"]["embedding"]
            print(f"类型: {embedding_field.get('type', 'N/A')}")
            if "dims" in embedding_field:
                vector_dim = embedding_field["dims"]
                print(f"维度: {vector_dim}")
            else:
                print("❓ 找不到向量维度信息")
        else:
            print("❓ 找不到embedding字段")
        
        # 检查mini_chunks字段是否存在
        print("\n📌 mini_chunks字段信息:")
        if "mini_chunks" in mapping[index_name]["mappings"]["properties"]:
            mini_chunks_field = mapping[index_name]["mappings"]["properties"]["mini_chunks"]
            print(f"类型: {mini_chunks_field.get('type', 'N/A')}")
            print(f"是否启用索引: {mini_chunks_field.get('enabled', 'N/A')}")
        else:
            print("❌ mini_chunks字段不存在")
        
        # 打印索引设置
        print("\n📌 索引设置:")
        try:
            print(f"分片数: {settings[index_name]['settings']['index']['number_of_shards']}")
            print(f"副本数: {settings[index_name]['settings']['index']['number_of_replicas']}")
        except KeyError:
            print("❓ 无法获取分片和副本设置")
        
        # 打印所有字段
        print("\n📌 索引字段列表:")
        for field_name, field_def in mapping[index_name]["mappings"]["properties"].items():
            field_type = field_def.get("type", "未知类型")
            print(f"- {field_name}: {field_type}")
        
        # 尝试获取一个文档样例
        print("\n📌 尝试获取一个文档样例:")
        try:
            search_result = es.search(index=index_name, size=1)
            if search_result["hits"]["total"]["value"] > 0:
                sample_doc = search_result["hits"]["hits"][0]["_source"]
                print("文档字段:")
                for key in sample_doc.keys():
                    print(f"- {key}")
                
                # 检查embedding字段
                if "embedding" in sample_doc:
                    embedding = sample_doc["embedding"]
                    if isinstance(embedding, list):
                        print(f"\nembedding是数组，长度为: {len(embedding)}")
                        print(f"前5个值: {embedding[:5]}")
                    else:
                        print(f"\nembedding不是数组，类型为: {type(embedding)}")
                
                # 检查mini_chunks字段
                if "mini_chunks" in sample_doc:
                    mini_chunks = sample_doc["mini_chunks"]
                    if isinstance(mini_chunks, list):
                        print(f"\nmini_chunks是数组，包含 {len(mini_chunks)} 个项目")
                        if mini_chunks:
                            print("第一个mini_chunk的字段:")
                            for key in mini_chunks[0].keys():
                                print(f"- {key}")
                    else:
                        print(f"\nmini_chunks不是数组，类型为: {type(mini_chunks)}")
            else:
                print("没有找到文档")
        except Exception as e:
            print(f"获取文档样例时出错: {e}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")

def main():
    parser = argparse.ArgumentParser(description="检查Elasticsearch环境")
    
    parser.add_argument("--host", default="localhost", help="ES主机")
    parser.add_argument("--port", default=9200, type=int, help="ES端口")
    parser.add_argument("--user", help="ES用户名")
    parser.add_argument("--pass", dest="password", help="ES密码")
    parser.add_argument("--index", default="knowledge_base_new", help="要检查的索引名称")
    
    args = parser.parse_args()
    
    # 检查ES环境
    check_es_environment(
        args.host, args.port, args.user, args.password, args.index
    )
    
    print("\n检查完成!")

if __name__ == "__main__":
    main()
