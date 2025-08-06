#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试Elasticsearch连接
"""

import requests
import socket
import time

def test_detailed_connection():
    """详细测试连接"""
    print("🔍 详细测试Elasticsearch连接...")
    
    # 测试不同的URL
    urls = [
        "http://localhost:9200",
        "http://127.0.0.1:9200",
        "http://localhost:9200/",
        "http://127.0.0.1:9200/"
    ]
    
    for url in urls:
        print(f"\n尝试连接: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    info = response.json()
                    print(f"✅ 连接成功!")
                    print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
                    print(f"   集群: {info.get('cluster_name', 'N/A')}")
                    print(f"   节点: {info.get('name', 'N/A')}")
                    return True
                except Exception as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应内容: {response.text[:200]}")
            else:
                print(f"❌ HTTP状态码异常: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接被拒绝: {e}")
        except requests.exceptions.Timeout as e:
            print(f"❌ 连接超时: {e}")
        except Exception as e:
            print(f"❌ 连接失败: {e}")
    
    return False

def test_cluster_health():
    """测试集群健康状态"""
    print("\n🔍 测试集群健康状态...")
    
    try:
        response = requests.get('http://localhost:9200/_cluster/health', timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ 集群健康检查成功")
            print(f"   状态: {health.get('status')}")
            print(f"   节点数: {health.get('number_of_nodes')}")
            print(f"   活跃分片: {health.get('active_shards')}")
            return True
        else:
            print(f"❌ 集群健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 集群健康检查异常: {e}")
        return False

def test_indices():
    """测试索引列表"""
    print("\n🔍 测试索引列表...")
    
    try:
        response = requests.get('http://localhost:9200/_cat/indices?v', timeout=10)
        if response.status_code == 200:
            print("✅ 索引列表获取成功")
            print("当前索引:")
            print(response.text)
            return True
        else:
            print(f"❌ 索引列表获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 索引列表获取异常: {e}")
        return False

def main():
    print("🚀 Elasticsearch 详细连接测试")
    print("=" * 40)
    
    # 测试基础连接
    if test_detailed_connection():
        print("\n✅ 基础连接成功")
        
        # 测试集群健康
        test_cluster_health()
        
        # 测试索引列表
        test_indices()
        
        print("\n🎉 ES运行正常，可以继续设置知识库")
        print("💡 运行: python es_setup.py")
    else:
        print("\n❌ ES连接失败")
        print("💡 可能的原因:")
        print("   1. ES还在启动中，请等待30-60秒")
        print("   2. ES启动失败，检查控制台日志")
        print("   3. 端口被其他程序占用")
        print("   4. 防火墙阻止连接")

if __name__ == "__main__":
    main() 