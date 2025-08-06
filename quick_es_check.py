#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查Elasticsearch状态
"""

import requests
import socket
import time

def quick_check():
    """快速检查ES状态"""
    print("🔍 快速检查Elasticsearch...")
    
    # 检查端口
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 9200))
        sock.close()
        
        if result == 0:
            print("✅ 端口9200已开放")
        else:
            print("❌ 端口9200未开放")
            print("💡 ES可能还在启动中，请等待30-60秒")
            return False
    except:
        print("❌ 端口检查失败")
        return False
    
    # 测试HTTP连接
    try:
        print("🔍 测试HTTP连接...")
        response = requests.get('http://localhost:9200', timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ ES连接成功!")
            print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
            print(f"   集群: {info.get('cluster_name', 'N/A')}")
            return True
        else:
            print(f"❌ HTTP响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接被拒绝 - ES可能还在启动")
        return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时 - ES可能还在启动")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def main():
    print("🚀 Elasticsearch 快速检查")
    print("=" * 30)
    
    if quick_check():
        print("\n✅ ES运行正常，可以继续下一步")
        print("💡 运行: python es_setup.py")
    else:
        print("\n❌ ES未就绪")
        print("💡 请确保ES已启动并等待30-60秒")

if __name__ == "__main__":
    main() 