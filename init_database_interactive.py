#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式数据库初始化脚本
"""

import pymysql
import os
import getpass

def get_mysql_config():
    """获取MySQL配置"""
    print("🔧 配置MySQL连接...")
    
    host = input("MySQL主机地址 (默认: localhost): ").strip() or "localhost"
    port = input("MySQL端口 (默认: 3306): ").strip() or "3306"
    user = input("MySQL用户名 (默认: root): ").strip() or "root"
    
    # 安全地获取密码
    password = getpass.getpass("MySQL密码: ")
    
    return {
        'host': host,
        'port': int(port),
        'user': user,
        'password': password,
        'charset': 'utf8mb4'
    }

def test_connection(config):
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
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
        return False

def init_database(config):
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
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

def main():
    """主函数"""
    print("🚀 数据库初始化工具")
    print("=" * 40)
    
    # 获取配置
    config = get_mysql_config()
    
    # 测试连接
    if not test_connection(config):
        print("❌ 无法连接到MySQL，请检查配置")
        return
    
    # 确认执行
    print("\n⚠️  即将执行数据库初始化，这将:")
    print("  1. 创建 knowledge_base 数据库")
    print("  2. 创建所有必要的表")
    print("  3. 插入测试数据")
    
    confirm = input("\n是否继续? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 操作已取消")
        return
    
    # 执行初始化
    if init_database(config):
        print("\n✅ 数据库初始化成功！")
        print("💡 现在可以启动Java应用了")
    else:
        print("\n❌ 数据库初始化失败！")

if __name__ == "__main__":
    main() 