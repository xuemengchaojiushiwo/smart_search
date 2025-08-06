#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查Elasticsearch进程状态
"""

import subprocess
import os

def check_es_process():
    """检查ES进程"""
    print("🔍 检查Elasticsearch进程...")
    
    try:
        # 检查Java进程
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq java.exe'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0 and 'java.exe' in result.stdout:
            print("✅ 发现Java进程")
            lines = result.stdout.strip().split('\n')
            java_count = 0
            for line in lines:
                if 'java.exe' in line:
                    java_count += 1
                    print(f"   {line.strip()}")
            
            print(f"\n📊 统计: 发现 {java_count} 个Java进程")
            
            if java_count > 0:
                print("💡 ES可能正在启动中，请耐心等待")
                print("💡 如果等待时间过长，可以:")
                print("   1. 检查ES启动日志")
                print("   2. 重启ES服务")
                return True
            else:
                print("❌ 未发现Java进程")
                return False
        else:
            print("❌ 未发现Java进程")
            return False
            
    except Exception as e:
        print(f"❌ 进程检查失败: {e}")
        return False

def check_es_logs():
    """检查ES日志"""
    print("\n🔍 检查Elasticsearch日志...")
    
    es_path = r"D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
    logs_path = os.path.join(es_path, "logs")
    
    if os.path.exists(logs_path):
        print(f"✅ 日志目录存在: {logs_path}")
        
        # 查找最新的日志文件
        log_files = []
        for file in os.listdir(logs_path):
            if file.endswith('.log'):
                log_files.append(file)
        
        if log_files:
            print(f"📄 发现 {len(log_files)} 个日志文件:")
            for file in log_files[:5]:  # 显示前5个
                print(f"   - {file}")
            
            # 尝试读取最新的日志
            latest_log = os.path.join(logs_path, log_files[0])
            try:
                with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"\n📋 最新日志内容 (最后10行):")
                        for line in lines[-10:]:
                            print(f"   {line.strip()}")
            except Exception as e:
                print(f"❌ 读取日志失败: {e}")
        else:
            print("ℹ️  暂无日志文件")
    else:
        print(f"❌ 日志目录不存在: {logs_path}")

def main():
    print("🚀 Elasticsearch 进程检查")
    print("=" * 40)
    
    if check_es_process():
        check_es_logs()
        
        print("\n💡 建议:")
        print("1. 如果ES正在启动，请等待5-10分钟")
        print("2. 如果启动时间过长，可以重启ES")
        print("3. 检查系统内存是否充足")
        print("4. 查看ES启动日志了解详细情况")
    else:
        print("\n❌ ES进程未运行")
        print("💡 请启动ES:")
        print("   cd D:\\xmc\\elasticsearch-9.1.0-windows-x86_64\\elasticsearch-9.1.0")
        print("   .\\bin\\elasticsearch.bat")

if __name__ == "__main__":
    main() 