#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
解决字符编码问题
"""

import pymysql
import os

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 数据库连接配置
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',  # 请根据实际情况修改密码
        'charset': 'utf8mb4'
    }
    
    try:
        # 连接MySQL（不指定数据库）
        print("📡 连接到MySQL...")
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # 读取SQL文件
        sql_file = "src/main/resources/db/init_fixed.sql"
        if not os.path.exists(sql_file):
            print(f"❌ SQL文件不存在: {sql_file}")
            return False
        
        print(f"📖 读取SQL文件: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句
        sql_statements = sql_content.split(';')
        
        print("🔧 执行SQL语句...")
        for i, statement in enumerate(sql_statements):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    print(f"✅ 执行语句 {i+1}: {statement[:50]}...")
                except Exception as e:
                    print(f"❌ 执行语句 {i+1} 失败: {e}")
                    print(f"   语句: {statement[:100]}...")
                    return False
        
        # 提交事务
        connection.commit()
        print("✅ 数据库初始化完成！")
        
        # 验证数据库和表是否创建成功
        print("\n🔍 验证数据库...")
        cursor.execute("SHOW DATABASES LIKE 'knowledge_base'")
        if cursor.fetchone():
            print("✅ knowledge_base 数据库创建成功")
        else:
            print("❌ knowledge_base 数据库创建失败")
            return False
        
        cursor.execute("USE knowledge_base")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✅ 创建了 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        print(f"✅ 类目数据: {category_count} 条")
        
        cursor.execute("SELECT COUNT(*) FROM knowledge")
        knowledge_count = cursor.fetchone()[0]
        print(f"✅ 知识数据: {knowledge_count} 条")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ 用户数据: {user_count} 条")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 数据库初始化验证完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

def test_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '',  # 请根据实际情况修改密码
        'charset': 'utf8mb4'
    }
    
    try:
        connection = pymysql.connect(**config)
        cursor = connection.cursor()
        
        # 测试查询
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        print(f"✅ MySQL连接成功，版本: {version}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        print("💡 请检查:")
        print("  1. MySQL服务是否启动")
        print("  2. 用户名密码是否正确")
        print("  3. 端口是否正确")
        return False

def main():
    """主函数"""
    print("🚀 数据库初始化工具")
    print("=" * 40)
    
    # 首先测试连接
    if not test_connection():
        return
    
    # 执行初始化
    if init_database():
        print("\n✅ 数据库初始化成功！")
        print("💡 现在可以启动Java应用了")
    else:
        print("\n❌ 数据库初始化失败！")

if __name__ == "__main__":
    main() 