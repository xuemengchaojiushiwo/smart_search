#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Elasticsearch认证连接
"""

import requests
import urllib3
import base64

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_es_with_auth():
    """测试ES认证连接"""
    print("🔍 测试Elasticsearch认证连接...")
    
    # 常见的默认用户名密码
    credentials = [
        ("elastic", "changeme"),
        ("elastic", "elastic"),
        ("admin", "admin"),
        ("", ""),  # 无认证
    ]
    
    urls = [
        "https://localhost:9200",
        "http://localhost:9200"
    ]
    
    for url in urls:
        print(f"\n尝试URL: {url}")
        
        for username, password in credentials:
            print(f"  尝试认证: {username if username else '无认证'}")
            
            try:
                if username and password:
                    # 使用基本认证
                    auth = (username, password)
                    response = requests.get(url, timeout=10, auth=auth, verify=False)
                else:
                    # 无认证
                    response = requests.get(url, timeout=10, verify=False)
                
                print(f"    状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        info = response.json()
                        print(f"    ✅ 连接成功!")
                        print(f"      版本: {info.get('version', {}).get('number', 'N/A')}")
                        print(f"      集群: {info.get('cluster_name', 'N/A')}")
                        print(f"      节点: {info.get('name', 'N/A')}")
                        
                        # 保存成功的认证信息
                        if username and password:
                            print(f"    💡 成功认证: {username}:{password}")
                        
                        return True, username, password
                        
                    except Exception as e:
                        print(f"    ❌ JSON解析失败: {e}")
                        print(f"    响应内容: {response.text[:200]}")
                        
                elif response.status_code == 401:
                    print(f"    ❌ 认证失败")
                else:
                    print(f"    ❌ HTTP状态码异常: {response.status_code}")
                    print(f"    响应内容: {response.text[:200]}")
                    
            except requests.exceptions.ConnectionError as e:
                print(f"    ❌ 连接被拒绝: {e}")
            except requests.exceptions.Timeout as e:
                print(f"    ❌ 连接超时: {e}")
            except Exception as e:
                print(f"    ❌ 连接失败: {e}")
    
    return False, None, None

def test_cluster_health_with_auth(username=None, password=None):
    """测试集群健康状态（带认证）"""
    print("\n🔍 测试集群健康状态...")
    
    urls = [
        "https://localhost:9200/_cluster/health",
        "http://localhost:9200/_cluster/health"
    ]
    
    for url in urls:
        try:
            print(f"尝试: {url}")
            
            if username and password:
                auth = (username, password)
                response = requests.get(url, timeout=10, auth=auth, verify=False)
            else:
                response = requests.get(url, timeout=10, verify=False)
                
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
    print("🚀 Elasticsearch 认证连接测试")
    print("=" * 40)
    
    success, username, password = test_es_with_auth()
    
    if success:
        print("\n✅ ES连接成功")
        test_cluster_health_with_auth(username, password)
        
        print("\n🎉 ES运行正常，可以继续设置知识库")
        print("💡 运行: python es_setup.py")
        
        if username and password:
            print(f"💡 认证信息: {username}:{password}")
    else:
        print("\n❌ ES连接失败")
        print("💡 可能的原因:")
        print("   1. ES需要认证，请检查用户名密码")
        print("   2. ES配置了HTTPS，需要SSL证书")
        print("   3. ES还在启动中")
        print("   4. 端口被其他程序占用")

if __name__ == "__main__":
    main() 