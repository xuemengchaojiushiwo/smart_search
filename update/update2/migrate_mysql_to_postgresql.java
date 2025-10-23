#!/usr/bin/env python3
"""
MySQL 到 PostgreSQL 数据迁移脚本
基于现有的 init_fixed.sql 结构
"""

import mysql.connector
import psycopg2
import json
from datetime import datetime
import sys

# MySQL 连接配置
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'xmc131455',
    'database': 'knowledge_base',
    'charset': 'utf8mb4'
}

# PostgreSQL 连接配置
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'password',
    'database': 'knowledge_base'
}

def connect_mysql():
    """连接 MySQL"""
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except Exception as e:
        print(f"MySQL 连接失败: {e}")
        sys.exit(1)

def connect_postgres():
    """连接 PostgreSQL"""
    try:
        return psycopg2.connect(**POSTGRES_CONFIG)
    except Exception as e:
        print(f"PostgreSQL 连接失败: {e}")
        sys.exit(1)

def migrate_users(mysql_conn, postgres_conn):
    """迁移用户数据"""
    print("迁移用户数据...")
    
    mysql_cursor = mysql_conn.cursor(dictionary=True)
    postgres_cursor = postgres_conn.cursor()
    
    mysql_cursor.execute("SELECT * FROM users WHERE deleted = 0")
    users = mysql_cursor.fetchall()
    
    for user in users:
        # 处理布尔值转换
        deleted = bool(user['deleted'])
        status = int(user['status']) if user['status'] is not None else 1
        
        postgres_cursor.execute("""
            INSERT INTO users (id, username, staffid, email, role, display_name, profile_picture, 
                             password, last_login, date_joined, staff_role, system_role, workspace, 
                             status, created_time, updated_time, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            user['id'], user['username'], user['staffid'], user['email'], user['role'],
            user['display_name'], user['profile_picture'], user['password'], user['last_login'],
            user['date_joined'], user['staff_role'], user['system_role'], user['workspace'],
            status, user['created_time'], user['updated_time'], deleted
        ))
    
    postgres_conn.commit()
    print(f"迁移了 {len(users)} 个用户")

def migrate_knowledge(mysql_conn, postgres_conn):
    """迁移知识数据"""
    print("迁移知识数据...")
    
    mysql_cursor = mysql_conn.cursor(dictionary=True)
    postgres_cursor = postgres_conn.cursor()
    
    mysql_cursor.execute("SELECT * FROM knowledge WHERE deleted = 0")
    knowledge_list = mysql_cursor.fetchall()
    
    for knowledge in knowledge_list:
        # 处理 JSON 字段
        tags = json.loads(knowledge['tags']) if knowledge['tags'] else []
        table_data = json.loads(knowledge['table_data']) if knowledge['table_data'] else {}
        
        # 处理布尔值
        deleted = bool(knowledge['deleted'])
        status = int(knowledge['status']) if knowledge['status'] is not None else 1
        
        postgres_cursor.execute("""
            INSERT INTO knowledge (id, name, description, parent_id, node_type, tags, table_data,
                                 effective_start_time, effective_end_time, status, created_by,
                                 created_time, updated_by, updated_time, search_count, download_count, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            knowledge['id'], knowledge['name'], knowledge['description'], knowledge['parent_id'],
            knowledge['node_type'], json.dumps(tags), json.dumps(table_data),
            knowledge['effective_start_time'], knowledge['effective_end_time'], status,
            knowledge['created_by'], knowledge['created_time'], knowledge['updated_by'],
            knowledge['updated_time'], knowledge['search_count'], knowledge['download_count'], deleted
        ))
    
    postgres_conn.commit()
    print(f"迁移了 {len(knowledge_list)} 个知识项")

def migrate_knowledge_workspace(mysql_conn, postgres_conn):
    """迁移知识工作空间关联"""
    print("迁移知识工作空间关联...")
    
    mysql_cursor = mysql_conn.cursor(dictionary=True)
    postgres_cursor = postgres_conn.cursor()
    
    mysql_cursor.execute("SELECT * FROM knowledge_workspace")
    relations = mysql_cursor.fetchall()
    
    for relation in relations:
        postgres_cursor.execute("""
            INSERT INTO knowledge_workspace (id, knowledge_id, workspace)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (relation['id'], relation['knowledge_id'], relation['workspace']))
    
    postgres_conn.commit()
    print(f"迁移了 {len(relations)} 个知识工作空间关联")

def migrate_attachments(mysql_conn, postgres_conn):
    """迁移附件数据"""
    print("迁移附件数据...")
    
    mysql_cursor = mysql_conn.cursor(dictionary=True)
    postgres_cursor = postgres_conn.cursor()
    
    mysql_cursor.execute("SELECT * FROM attachments WHERE deleted = 0")
    attachments = mysql_cursor.fetchall()
    
    for attachment in attachments:
        deleted = bool(attachment['deleted'])
        
        postgres_cursor.execute("""
            INSERT INTO attachments (id, knowledge_id, file_name, file_path, file_size, file_type,
                                   upload_time, file_hash, version_id, version_number, download_count, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (
            attachment['id'], attachment['knowledge_id'], attachment['file_name'], attachment['file_path'],
            attachment['file_size'], attachment['file_type'], attachment['upload_time'], attachment['file_hash'],
            attachment['version_id'], attachment['version_number'], attachment['download_count'], deleted
        ))
    
    postgres_conn.commit()
    print(f"迁移了 {len(attachments)} 个附件")

def migrate_other_tables(mysql_conn, postgres_conn):
    """迁移其他表"""
    tables = [
        'knowledge_versions', 'knowledge_likes', 'knowledge_favorites', 
        'knowledge_feedbacks', 'search_history', 'chat_feedbacks',
        'chat_sessions', 'chat_messages', 'user_dept_role', 'workspaces'
    ]
    
    for table in tables:
        print(f"迁移 {table} 表...")
        
        mysql_cursor = mysql_conn.cursor(dictionary=True)
        postgres_cursor = postgres_conn.cursor()
        
        try:
            mysql_cursor.execute(f"SELECT * FROM {table}")
            rows = mysql_cursor.fetchall()
            
            if not rows:
                print(f"  {table} 表为空，跳过")
                continue
            
            # 获取列名
            columns = list(rows[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            
            for row in rows:
                values = []
                for col in columns:
                    value = row[col]
                    # 处理布尔值
                    if col == 'deleted' and value is not None:
                        value = bool(value)
                    elif col in ['status', 'attitude', 'message_count', 'result_count', 'search_count', 'download_count'] and value is not None:
                        value = int(value)
                    values.append(value)
                
                postgres_cursor.execute(f"""
                    INSERT INTO {table} ({column_names})
                    VALUES ({placeholders})
                    ON CONFLICT (id) DO NOTHING
                """, values)
            
            postgres_conn.commit()
            print(f"  迁移了 {len(rows)} 条记录")
            
        except Exception as e:
            print(f"  迁移 {table} 失败: {e}")
            postgres_conn.rollback()

def main():
    """主函数"""
    print("开始 MySQL 到 PostgreSQL 数据迁移...")
    
    # 连接数据库
    mysql_conn = connect_mysql()
    postgres_conn = connect_postgres()
    
    try:
        # 按顺序迁移数据
        migrate_users(mysql_conn, postgres_conn)
        migrate_knowledge(mysql_conn, postgres_conn)
        migrate_knowledge_workspace(mysql_conn, postgres_conn)
        migrate_attachments(mysql_conn, postgres_conn)
        migrate_other_tables(mysql_conn, postgres_conn)
        
        print("数据迁移完成！")
        
    except Exception as e:
        print(f"迁移过程中出现错误: {e}")
        postgres_conn.rollback()
    finally:
        mysql_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    main()
