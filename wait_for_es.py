#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待Elasticsearch启动完成
"""

import requests
import time
import socket

def wait_for_es():
    """等待ES启动完成"""
    print("⏳ 等待Elasticsearch启动完成...")
    print("💡 这通常需要30-60秒")
    
    max_wait_time = 120  # 最大等待2分钟
    check_interval = 5   # 每5秒检查一次
    
    for i in range(0, max_wait_time, check_interval):
        print(f"\n🔍 第 {i//check_interval + 1} 次检查 ({i}秒)...")
        
        # 检查端口
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 9200))
            sock.close()
            
            if result != 0:
                print("   ⏳ 端口9200还未开放，继续等待...")
                time.sleep(check_interval)
                continue
        except:
            print("   ⏳ 端口检查失败，继续等待...")
            time.sleep(check_interval)
            continue
        
        # 检查HTTP连接
        try:
            response = requests.get('http://localhost:9200', timeout=5)
            if response.status_code == 200:
                try:
                    info = response.json()
                    print(f"✅ ES启动完成!")
                    print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
                    print(f"   集群: {info.get('cluster_name', 'N/A')}")
                    print(f"   节点: {info.get('name', 'N/A')}")
                    return True
                except:
                    print("   ⏳ ES响应格式异常，继续等待...")
            else:
                print(f"   ⏳ HTTP状态码异常: {response.status_code}，继续等待...")
                
        except requests.exceptions.ConnectionError:
            print("   ⏳ 连接被拒绝，ES还在启动中...")
        except requests.exceptions.Timeout:
            print("   ⏳ 连接超时，ES还在启动中...")
        except Exception as e:
            print(f"   ⏳ 连接异常: {e}，继续等待...")
        
        time.sleep(check_interval)
    
    print(f"\n❌ 等待超时 ({max_wait_time}秒)")
    print("💡 请检查ES是否正常启动")
    return False

def main():
    print("🚀 等待Elasticsearch启动")
    print("=" * 30)
    
    if wait_for_es():
        print("\n🎉 ES启动完成，可以继续下一步")
        print("💡 运行: python es_setup.py")
    else:
        print("\n❌ ES启动超时")
        print("💡 请检查ES启动日志")

if __name__ == "__main__":
    main() 