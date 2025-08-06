#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elasticsearch 连接诊断脚本
"""

import requests
import socket
import subprocess
import time
import os

def check_port_open():
    """检查端口是否开放"""
    print("🔍 检查端口9200是否开放...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 9200))
        sock.close()
        
        if result == 0:
            print("✅ 端口9200已开放")
            return True
        else:
            print("❌ 端口9200未开放")
            return False
            
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")
        return False

def check_es_process():
    """检查ES进程是否运行"""
    print("\n🔍 检查Elasticsearch进程...")
    
    try:
        # 检查Java进程
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq java.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if 'java.exe' in result.stdout:
            print("✅ 发现Java进程")
            # 显示Java进程详情
            java_processes = [line for line in result.stdout.split('\n') if 'java.exe' in line]
            for process in java_processes[:3]:  # 显示前3个
                print(f"   {process.strip()}")
            return True
        else:
            print("❌ 未发现Java进程")
            return False
            
    except Exception as e:
        print(f"❌ 进程检查失败: {e}")
        return False

def check_es_config():
    """检查ES配置文件"""
    print("\n🔍 检查Elasticsearch配置...")
    
    es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
    
    # 检查目录是否存在
    if os.path.exists(es_path):
        print(f"✅ ES目录存在: {es_path}")
        
        # 检查关键文件
        key_files = [
            "bin\\elasticsearch.bat",
            "config\\elasticsearch.yml",
            "config\\jvm.options"
        ]
        
        for file in key_files:
            full_path = os.path.join(es_path, file)
            if os.path.exists(full_path):
                print(f"✅ {file} 存在")
            else:
                print(f"❌ {file} 不存在")
    else:
        print(f"❌ ES目录不存在: {es_path}")
        return False
    
    return True

def test_http_connection():
    """测试HTTP连接"""
    print("\n🔍 测试HTTP连接...")
    
    urls = [
        "http://localhost:9200",
        "http://127.0.0.1:9200"
    ]
    
    for url in urls:
        try:
            print(f"   尝试连接: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} 连接成功")
                info = response.json()
                print(f"   版本: {info.get('version', {}).get('number', 'N/A')}")
                print(f"   集群: {info.get('cluster_name', 'N/A')}")
                return True
            else:
                print(f"❌ {url} 响应异常: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {url} 连接被拒绝")
        except requests.exceptions.Timeout:
            print(f"❌ {url} 连接超时")
        except Exception as e:
            print(f"❌ {url} 连接失败: {e}")
    
    return False

def check_system_resources():
    """检查系统资源"""
    print("\n🔍 检查系统资源...")
    
    try:
        # 检查内存使用
        result = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                total_memory = int(lines[1]) / (1024**3)  # 转换为GB
                print(f"✅ 总内存: {total_memory:.1f} GB")
                
                if total_memory < 4:
                    print("⚠️  内存可能不足，建议至少4GB")
        
        # 检查磁盘空间
        es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
        if os.path.exists(es_path):
            free_space = os.statvfs(es_path).f_frsize * os.statvfs(es_path).f_bavail
            free_gb = free_space / (1024**3)
            print(f"✅ 可用磁盘空间: {free_gb:.1f} GB")
            
            if free_gb < 1:
                print("⚠️  磁盘空间可能不足")
                
    except Exception as e:
        print(f"❌ 资源检查失败: {e}")

def suggest_solutions():
    """提供解决方案建议"""
    print("\n💡 解决方案建议:")
    print("=" * 50)
    
    print("1. 启动Elasticsearch:")
    print("   cd D:\\xmc\\elasticsearch-9.1.0-windows-x86_64\\elasticsearch-9.1.0")
    print("   .\\bin\\elasticsearch.bat")
    print("")
    
    print("2. 等待启动完成（通常需要30-60秒）")
    print("")
    
    print("3. 检查启动日志:")
    print("   查看控制台输出或logs目录下的日志文件")
    print("")
    
    print("4. 常见问题:")
    print("   - 内存不足: 编辑config\\jvm.options，设置-Xms1g -Xmx1g")
    print("   - 端口被占用: 检查是否有其他ES实例运行")
    print("   - 权限问题: 以管理员身份运行")
    print("")
    
    print("5. 验证启动:")
    print("   python test_es_status.py")

def main():
    """主函数"""
    print("🚀 Elasticsearch 连接诊断")
    print("=" * 50)
    
    # 检查配置
    if not check_es_config():
        print("\n❌ ES配置有问题，请检查安装路径")
        suggest_solutions()
        return
    
    # 检查系统资源
    check_system_resources()
    
    # 检查进程
    if not check_es_process():
        print("\n❌ ES进程未运行")
        suggest_solutions()
        return
    
    # 检查端口
    if not check_port_open():
        print("\n❌ ES端口未开放")
        suggest_solutions()
        return
    
    # 测试HTTP连接
    if not test_http_connection():
        print("\n❌ HTTP连接失败")
        suggest_solutions()
        return
    
    print("\n✅ 所有检查通过，ES应该正常运行")
    print("💡 如果仍有问题，请检查ES启动日志")

if __name__ == "__main__":
    main() 