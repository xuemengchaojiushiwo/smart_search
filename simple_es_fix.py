#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Elasticsearch修复脚本
"""

import os
import subprocess
import time
import requests

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

def fix_es_config():
    """修复ES配置"""
    print("\n🔧 修复ES配置...")
    
    es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
    config_file = os.path.join(es_path, "config", "elasticsearch.yml")
    
    # 简化的配置
    config_content = """# 基本配置
cluster.name: elasticsearch
node.name: node-1

# 网络配置
network.host: localhost
http.port: 9200

# 禁用安全功能
xpack.security.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# 开发环境设置
discovery.type: single-node
"""
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ 配置已更新")
        return True
    except Exception as e:
        print(f"❌ 配置更新失败: {e}")
        return False

def restart_es():
    """重启ES"""
    print("\n🔄 重启ES...")
    
    # 停止ES
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'java.exe'], shell=True)
        time.sleep(3)
        print("✅ ES已停止")
    except:
        print("ℹ️  未发现ES进程")
    
    # 启动ES
    es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
    try:
        subprocess.Popen([
            os.path.join(es_path, "bin", "elasticsearch.bat")
        ], cwd=es_path)
        print("✅ ES启动命令已执行")
        return True
    except Exception as e:
        print(f"❌ 启动ES失败: {e}")
        return False

def wait_and_test():
    """等待并测试"""
    print("\n⏳ 等待ES启动...")
    
    for i in range(12):  # 等待60秒
        print(f"   检查 {i+1}/12...")
        time.sleep(5)
        
        if check_es_status():
            print("\n🎉 ES修复成功!")
            return True
    
    print("\n❌ ES启动超时")
    return False

def main():
    print("🚀 简化版ES修复工具")
    print("=" * 30)
    
    # 检查当前状态
    if check_es_status():
        print("\n✅ ES已经正常运行")
        return
    
    # 修复配置
    if not fix_es_config():
        print("❌ 配置修复失败")
        return
    
    # 重启ES
    if not restart_es():
        print("❌ ES重启失败")
        return
    
    # 等待并测试
    if wait_and_test():
        print("💡 现在可以运行: python es_setup.py")
    else:
        print("💡 请手动检查ES状态")

if __name__ == "__main__":
    main() 