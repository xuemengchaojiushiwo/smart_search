#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Elasticsearch HTTPS连接
"""

import requests
import urllib3
import socket

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_es_https():
    """测试ES HTTPS连接"""
    print("🔍 测试Elasticsearch HTTPS连接...")
    
    # 测试不同的URL
    urls = [
        "https://localhost:9200",
        "https://127.0.0.1:9200",
        "http://localhost:9200",  # 也试试HTTP
        "http://127.0.0.1:9200"
    ]
    
    for url in urls:
        print(f"\n尝试连接: {url}")
        try:
            # 对于HTTPS，禁用SSL验证
            if url.startswith('https'):
                response = requests.get(url, timeout=10, verify=False)
            else:
                response = requests.get(url, timeout=10)
                
            print(f"状态码: {response.status_code}")
            
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

def test_cluster_health_https():
    """测试集群健康状态（HTTPS）"""
    print("\n🔍 测试集群健康状态...")
    
    urls = [
        "https://localhost:9200/_cluster/health",
        "http://localhost:9200/_cluster/health"
    ]
    
    for url in urls:
        try:
            print(f"尝试: {url}")
            if url.startswith('https'):
                response = requests.get(url, timeout=10, verify=False)
            else:
                response = requests.get(url, timeout=10)
                
            if response.status_code == 200:
                health = response.json()
                print(f"✅ 集群健康检查成功")
                print(f"   状态: {health.get('status')}")
                print(f"   节点数: {health.get('number_of_nodes')}")
                print(f"   活跃分片: {health.get('active_shards')}")
                return True
            else:
                print(f"❌ 集群健康检查失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 集群健康检查异常: {e}")
    
    return False

def main():
    print("🚀 Elasticsearch HTTPS 连接测试")
    print("=" * 40)
    
    if test_es_https():
        print("\n✅ ES连接成功")
        test_cluster_health_https()
        
        print("\n🎉 ES运行正常，可以继续设置知识库")
        print("💡 运行: python es_setup.py")
    else:
        print("\n❌ ES连接失败")
        print("💡 可能的原因:")
        print("   1. ES配置了HTTPS，需要SSL证书")
        print("   2. ES还在启动中")
        print("   3. 端口被其他程序占用")

if __name__ == "__main__":
    main() 