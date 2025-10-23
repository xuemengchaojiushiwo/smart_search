#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复 psycopg2 问题
"""

import subprocess
import sys
import os

def quick_fix():
    """快速修复 psycopg2"""
    print("🔧 快速修复 psycopg2 问题...")
    
    try:
        # 1. 卸载可能冲突的包
        print("1. 卸载可能冲突的包...")
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "psycopg2", "-y"], 
                      capture_output=True)
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "psycopg2-binary", "-y"], 
                      capture_output=True)
        
        # 2. 安装 psycopg2-binary
        print("2. 安装 psycopg2-binary...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ psycopg2-binary 安装成功")
        else:
            print(f"❌ 安装失败: {result.stderr}")
            return False
        
        # 3. 验证安装
        print("3. 验证安装...")
        try:
            import psycopg2
            from psycopg2 import _psycopg
            print(f"✅ psycopg2 安装成功，版本: {psycopg2.__version__}")
            return True
        except ImportError as e:
            print(f"❌ 验证失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 修复过程中发生错误: {e}")
        return False

def test_connection():
    """测试数据库连接"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres", 
            password="admin",
            database="smart_search"
        )
        print("✅ 数据库连接测试成功")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("psycopg2 快速修复工具")
    print("=" * 50)
    
    if quick_fix():
        print("\n🎉 修复成功！")
        test_connection()
    else:
        print("\n❌ 修复失败，请查看错误信息")
        print("\n手动修复命令:")
        print("pip uninstall psycopg2 psycopg2-binary -y")
        print("pip install psycopg2-binary==2.9.9")
    
    print("\n" + "=" * 50)
