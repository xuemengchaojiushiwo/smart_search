#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Elasticsearch状态
"""

import requests
import json

def test_es_connection():
    """测试ES连接"""
    print("🔍 测试Elasticsearch连接...")
    
    try:
        # 测试基础连接
        response = requests.get('http://localhost:9200', timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ Elasticsearch连接成功")
            print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
            print(f"   集群名称: {info.get('cluster_name', 'N/A')}")
            print(f"   节点名称: {info.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ 连接失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Elasticsearch")
        print("💡 请确保ES已启动:")
        print("   cd D:\\xmc\\elasticsearch-9.1.0-windows-x86_64\\elasticsearch-9.1.0")
        print("   .\\bin\\elasticsearch.bat")
        return False
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

def test_cluster_health():
    """测试集群健康状态"""
    print("\n🏥 测试集群健康状态...")
    
    try:
        response = requests.get('http://localhost:9200/_cluster/health', timeout=10)
        if response.status_code == 200:
            health = response.json()
            status = health.get('status', 'unknown')
            print(f"✅ 集群状态: {status}")
            print(f"   节点数量: {health.get('number_of_nodes', 0)}")
            print(f"   活跃分片: {health.get('active_shards', 0)}")
            print(f"   总数据节点: {health.get('number_of_data_nodes', 0)}")
            return status in ['green', 'yellow']
        else:
            print(f"❌ 获取集群状态失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 集群健康检查失败: {e}")
        return False

def test_indices():
    """测试索引列表"""
    print("\n📚 检查索引列表...")
    
    try:
        response = requests.get('http://localhost:9200/_cat/indices?v', timeout=10)
        if response.status_code == 200:
            indices = response.text.strip()
            if indices:
                print("✅ 发现以下索引:")
                print(indices)
            else:
                print("ℹ️  暂无索引")
            return True
        else:
            print(f"❌ 获取索引列表失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 索引检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Elasticsearch 状态检查")
    print("=" * 40)
    
    # 测试连接
    if not test_es_connection():
        return
    
    # 测试集群健康
    if not test_cluster_health():
        print("⚠️  集群状态异常，但ES已启动")
    
    # 测试索引
    test_indices()
    
    print("\n" + "=" * 40)
    print("✅ Elasticsearch状态检查完成")
    print("\n💡 下一步操作:")
    print("1. 如果ES正常启动，运行: python es_setup.py")
    print("2. 访问管理界面: http://localhost:9200/_cat/indices?v")
    print("3. 查看集群健康: http://localhost:9200/_cluster/health")

if __name__ == "__main__":
    main() 