#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复Elasticsearch配置
"""

import os
import shutil
import subprocess
import time
import requests

def backup_config():
    """备份原始配置"""
    print("📦 备份原始配置...")
    
    es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
    config_file = os.path.join(es_path, "config", "elasticsearch.yml")
    backup_file = os.path.join(es_path, "config", "elasticsearch.yml.backup")
    
    if os.path.exists(config_file):
        shutil.copy2(config_file, backup_file)
        print(f"✅ 配置已备份到: {backup_file}")
        return True
    else:
        print(f"❌ 配置文件不存在: {config_file}")
        return False

def modify_config():
    """修改ES配置"""
    print("\n🔧 修改ES配置...")
    
    es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
    config_file = os.path.join(es_path, "config", "elasticsearch.yml")
    
    # 新的配置内容
    new_config = """# 基本配置
cluster.name: elasticsearch
node.name: node-1
path.data: data
path.logs: logs

# 网络配置
network.host: localhost
http.port: 9200

# 禁用安全功能（开发环境）
xpack.security.enabled: false
xpack.security.http.ssl.enabled: false
xpack.security.transport.ssl.enabled: false

# 禁用X-Pack功能
xpack.monitoring.enabled: false
xpack.watcher.enabled: false
xpack.ml.enabled: false

# 开发环境设置
discovery.type: single-node
"""
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(new_config)
        print(f"✅ 配置已更新: {config_file}")
        return True
    except Exception as e:
        print(f"❌ 配置更新失败: {e}")
        return False

def stop_es():
    """停止ES服务"""
    print("\n🛑 停止Elasticsearch...")
    
    try:
        # 查找并结束Java进程
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq java.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'java.exe' in result.stdout:
            print("发现Java进程，正在停止...")
            subprocess.run(['taskkill', '/F', '/IM', 'java.exe'], shell=True)
            time.sleep(5)  # 等待进程结束
            print("✅ ES服务已停止")
        else:
            print("ℹ️  未发现Java进程")
        
        return True
    except Exception as e:
        print(f"❌ 停止ES失败: {e}")
        return False

def start_es():
    """启动ES服务"""
    print("\n🚀 启动Elasticsearch...")
    
    es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
    
    try:
        # 启动ES
        subprocess.Popen([
            os.path.join(es_path, "bin", "elasticsearch.bat")
        ], cwd=es_path)
        
        print("✅ ES启动命令已执行")
        print("💡 请等待30-60秒让ES完全启动")
        return True
    except Exception as e:
        print(f"❌ 启动ES失败: {e}")
        return False

def wait_for_es():
    """等待ES启动"""
    print("\n⏳ 等待ES启动完成...")
    
    max_wait = 120  # 最大等待2分钟
    check_interval = 5  # 每5秒检查一次
    
    for i in range(0, max_wait, check_interval):
        print(f"   检查 {i//check_interval + 1} ({i}秒)...")
        
        try:
            response = requests.get('http://localhost:9200', timeout=5)
            if response.status_code == 200:
                info = response.json()
                print(f"✅ ES启动完成!")
                print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
                print(f"   集群: {info.get('cluster_name', 'N/A')}")
                return True
        except:
            pass
        
        time.sleep(check_interval)
    
    print(f"❌ 等待超时 ({max_wait}秒)")
    return False

def test_connection():
    """测试连接"""
    print("\n🔍 测试ES连接...")
    
    try:
        response = requests.get('http://localhost:9200', timeout=10)
        if response.status_code == 200:
            info = response.json()
            print("✅ ES连接成功!")
            print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
            print(f"   集群: {info.get('cluster_name', 'N/A')}")
            return True
        else:
            print(f"❌ HTTP状态码异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def main():
    print("🚀 Elasticsearch 配置修复工具")
    print("=" * 40)
    
    # 1. 备份配置
    if not backup_config():
        print("❌ 备份失败，退出")
        return
    
    # 2. 修改配置
    if not modify_config():
        print("❌ 配置修改失败，退出")
        return
    
    # 3. 停止ES
    if not stop_es():
        print("❌ 停止ES失败，退出")
        return
    
    # 4. 启动ES
    if not start_es():
        print("❌ 启动ES失败，退出")
        return
    
    # 5. 等待启动
    if not wait_for_es():
        print("❌ ES启动超时")
        print("💡 请手动检查ES状态")
        return
    
    # 6. 测试连接
    if not test_connection():
        print("❌ 连接测试失败")
        return
    
    print("\n🎉 ES配置修复完成!")
    print("💡 现在可以运行: python es_setup.py")

if __name__ == "__main__":
    main() 