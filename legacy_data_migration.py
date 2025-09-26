#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史系统数据迁移工具
从 SQLite3 迁移到 MySQL
"""

import sqlite3
import mysql.connector
import json
import re
from datetime import datetime
import os
import sys
import logging

class LegacyDataMigration:
    def __init__(self, sqlite_db_path, mysql_config):
        self.sqlite_db_path = sqlite_db_path
        self.mysql_config = mysql_config
        self.mysql_conn = None
        self.sqlite_conn = None
        self.id_mapping = {}  # 存储旧ID到新ID的映射
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
        
    def connect_databases(self):
        """连接数据库"""
        try:
            # 连接 SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            print(f"✅ 已连接 SQLite 数据库: {self.sqlite_db_path}")
            
            # 连接 MySQL（强制使用 utf8mb4，避免中文/emoji 写入报错 1366）
            self.mysql_conn = mysql.connector.connect(
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                use_unicode=True,
                get_warnings=True,
                **self.mysql_config
            )
            # 双保险：设置会话字符集
            try:
                cur = self.mysql_conn.cursor()
                cur.execute("SET NAMES utf8mb4")
                cur.execute("SET CHARACTER SET utf8mb4")
                cur.execute("SET character_set_connection=utf8mb4")
                cur.close()
            except Exception:
                pass
            print(f"✅ 已连接 MySQL 数据库: {self.mysql_config['database']}")
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            sys.exit(1)

    def ensure_target_schema(self):
        """确保目标库存在迁移所需的新字段（幂等）。"""
        cursor = self.mysql_conn.cursor()
        add_columns_sql = [
            "ALTER TABLE users ADD COLUMN display_name VARCHAR(150) NULL",
            "ALTER TABLE users ADD COLUMN profile_picture VARCHAR(255) NULL",
            "ALTER TABLE users ADD COLUMN password VARCHAR(255) NULL",
            "ALTER TABLE users ADD COLUMN last_login DATETIME NULL",
            "ALTER TABLE users ADD COLUMN date_joined DATETIME NULL",
        ]
        for stmt in add_columns_sql:
            try:
                cursor.execute(stmt)
            except Exception as e:
                # 已存在则忽略
                if 'Duplicate column name' in str(e) or 'exists' in str(e).lower():
                    continue
                raise
        self.mysql_conn.commit()

    def _sqlite_columns(self, table_name: str):
        """读取 SQLite 表字段名集合。"""
        cur = self.sqlite_conn.cursor()
        cur.execute(f"PRAGMA table_info('{table_name}')")
        return {row[1] for row in cur.fetchall()}  # row[1] is column name
    
    def _clean_text(self, value, ctx: str):
        """将文本清洗为安全的 utf-8 内容，并在发生修复时打印日志。"""
        if value is None:
            return None
        if isinstance(value, (bytes, bytearray)):
            for enc in ('utf-8', 'gbk', 'latin1'):
                try:
                    decoded = bytes(value).decode(enc)
                    logging.warning(f"文本解码: {ctx} 使用 {enc} -> utf-8")
                    return decoded
                except Exception:
                    continue
            try:
                return bytes(value).decode('utf-8', errors='replace')
            except Exception:
                return str(value)
        try:
            value.encode('utf-8')
            return value
        except Exception:
            cleaned = value.encode('utf-8', errors='replace').decode('utf-8')
            logging.warning(f"文本替换: {ctx} 存在非utf8字符，已安全替换。原长={len(value)} 清洗后={len(cleaned)}")
            return cleaned
    
    def parse_path_to_hierarchy(self, path):
        """
        解析 path 编码为层级结构
        例如: 00010001000P00030004 -> [1, 1, 16, 3, 4]
        或者简单的: 0001 -> [1], 00010001 -> [1, 1]
        """
        if not path:
            return []
        
        hierarchy = []
        # 每4个字符为一个层级
        for i in range(0, len(path), 4):
            if i + 4 <= len(path):
                segment = path[i:i+4]
                if segment.isdigit():
                    hierarchy.append(int(segment))
                else:
                    # 处理包含字母的情况
                    for c in segment:
                        if c.isalpha():
                            hierarchy.append(ord(c) - ord('A') + 10)
                        elif c.isdigit():
                            hierarchy.append(int(c))
        
        return hierarchy
    
    def migrate_users(self):
        """迁移用户数据"""
        print("\n🔄 开始迁移用户数据...")
        
        cursor = self.sqlite_conn.cursor()
        cols = self._sqlite_columns('app_user')
        select_fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            ('password' if 'password' in cols else "NULL AS password"),
            ('last_login' if 'last_login' in cols else "NULL AS last_login"),
            ('date_joined' if 'date_joined' in cols else "datetime('now') AS date_joined"),
            ('is_active' if 'is_active' in cols else "1 AS is_active"),
            ('display_name' if 'display_name' in cols else "NULL AS display_name"),
            ('profile_picture' if 'profile_picture' in cols else "NULL AS profile_picture"),
            ('role' if 'role' in cols else "NULL AS role"),
        ]
        cursor.execute(f"SELECT {', '.join(select_fields)} FROM app_user")
        users = cursor.fetchall()
        
        mysql_cursor = self.mysql_conn.cursor()
        
        for user in users:
            old_id, username, email, first_name, last_name, password, last_login, date_joined, is_active, display_name, profile_picture, role = user
            
            # 生成新的用户ID
            mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM users")
            new_id = mysql_cursor.fetchone()[0]
            
            # 插入用户数据
            insert_sql = """
            INSERT INTO users (id, username, email, staffid, system_role, display_name, profile_picture, role, password, last_login, status, created_time, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                new_id,
                username or '',
                email or '',
                username or '',  # 使用 username 作为 staffid
                'ADMIN' if (role or '').upper() == 'ADMIN' else 'USER',  # 默认或按历史role
                display_name,
                profile_picture,
                role,
                password,
                last_login,
                1 if is_active else 0,
                date_joined or datetime.now(),
                0
            )
            
            mysql_cursor.execute(insert_sql, values)
            self.id_mapping[f"user_{old_id}"] = new_id
            
        self.mysql_conn.commit()
        print(f"✅ 用户数据迁移完成: {len(users)} 条记录")
    
    def migrate_categories(self):
        """迁移分类数据 (转换为 knowledge 表的 folder 类型)"""
        print("\n🔄 开始迁移分类数据...")
        
        cursor = self.sqlite_conn.cursor()
        cols = self._sqlite_columns('app_category')
        select_fields = [
            'id', 'name', 'path', 'depth',
            ('created' if 'created' in cols else "datetime('now') AS created"),
            ('updated' if 'updated' in cols else "NULL AS updated"),
        ]
        cursor.execute(f"SELECT {', '.join(select_fields)} FROM app_category ORDER BY length(path), path")
        categories = cursor.fetchall()
        
        mysql_cursor = self.mysql_conn.cursor()
        
        # 先创建所有分类节点，不设置 parent_id
        for category in categories:
            old_id, name, path, depth, created, updated = category
            
            # 生成新的ID
            mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM knowledge")
            new_id = mysql_cursor.fetchone()[0]
            
            # 根据path找到父节点
            parent_id = None
            if depth > 0:  # 如果深度大于0，说明有父节点
                # 截取父节点的path
                if len(path) >= 4:  # 确保path长度足够
                    parent_path = path[:-4]  # 去掉最后4个字符即为父节点path
                    cursor.execute("SELECT id FROM app_category WHERE path = ?", (parent_path,))
                    parent_result = cursor.fetchone()
                    if parent_result:
                        parent_old_id = parent_result[0]
                        if f"category_{parent_old_id}" in self.id_mapping:
                            parent_id = self.id_mapping[f"category_{parent_old_id}"]
            
            insert_sql = """
            INSERT INTO knowledge (id, name, parent_id, node_type, created_by, created_time, updated_time, status, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                new_id,
                name or '',
                parent_id,  # 直接设置parent_id
                'folder',
                'admin',  # 默认创建人
                created or datetime.now(),
                updated,
                1,
                0
            )
            
            mysql_cursor.execute(insert_sql, values)
            self.id_mapping[f"category_{old_id}"] = new_id
            print(f"  创建分类: id={new_id}, name={name}, parent_id={parent_id}, path={path}, depth={depth}")
            
        self.mysql_conn.commit()
        print(f"✅ 分类数据迁移完成: {len(categories)} 条记录")
    
    def migrate_content(self):
        """迁移内容数据"""
        print("\n🔄 开始迁移内容数据...")
        
        cursor = self.sqlite_conn.cursor()
        cols = self._sqlite_columns('app_contentitem')
        # 兼容历史命名：expired 或 expir_date
        expired_expr = (
            'expired' if 'expired' in cols else (
                'expir_date AS expired' if 'expir_date' in cols else "NULL AS expired"
            )
        )
        select_fields = [
            'id', 'title', 'text',
            ('keywords' if 'keywords' in cols else "NULL AS keywords"),
            ('created' if 'created' in cols else "datetime('now') AS created"),
            ('updated' if 'updated' in cols else "NULL AS updated"),
            expired_expr,
            ('category_id' if 'category_id' in cols else "NULL AS category_id"),
            ('creator_id' if 'creator_id' in cols else "NULL AS creator_id"),
        ]
        cursor.execute(f"SELECT {', '.join(select_fields)} FROM app_contentitem")
        contents = cursor.fetchall()
        
        mysql_cursor = self.mysql_conn.cursor()
        
        for content in contents:
            old_id, title, text, keywords, created, updated, expired, category_id, creator_id = content
            safe_title = self._clean_text(title, f"content.title(id={old_id})")
            safe_text = self._clean_text(text, f"content.text(id={old_id})")
            
            # 生成新的ID
            mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM knowledge")
            new_id = mysql_cursor.fetchone()[0]
            
            # 转换标签
            tags = []
            if keywords:
                tags = [tag.strip() for tag in keywords.split(',') if tag.strip()]
            
            # 获取父分类ID
            parent_id = None
            if category_id:
                # 打印调试信息
                print(f"  内容 {old_id}: 关联分类ID={category_id}, 映射键={f'category_{category_id}'}")
                if f"category_{category_id}" in self.id_mapping:
                    parent_id = self.id_mapping[f"category_{category_id}"]
                    print(f"  内容 {old_id}: 找到父分类ID={parent_id}")
                else:
                    print(f"  内容 {old_id}: 未找到父分类映射")
                    # 尝试查询分类是否存在
                    cursor.execute("SELECT id, name, path FROM app_category WHERE id = ?", (category_id,))
                    cat_result = cursor.fetchone()
                    if cat_result:
                        print(f"  分类存在但未映射: {cat_result}")
                        
            # 获取创建者ID，使用creator_id关联app_user表的username
            created_by = "admin"  # 默认创建者
            if creator_id:
                # 查询app_user表中对应的username
                creator_cursor = self.sqlite_conn.cursor()
                creator_cursor.execute("SELECT username FROM app_user WHERE id = ?", (creator_id,))
                creator_result = creator_cursor.fetchone()
                
                if creator_result and creator_result[0]:
                    username = creator_result[0]
                    # 在新表中查询对应的用户ID
                    mysql_cursor.execute("SELECT id FROM users WHERE staffid = %s", (username,))
                    user_result = mysql_cursor.fetchone()
                    if user_result:
                        created_by = username
                        print(f"  内容 {old_id}: 找到创建者 {username}, created_by={created_by}")
                    else:
                        print(f"  内容 {old_id}: 用户 {username} 在新系统中不存在或没有staffid")
                else:
                    print(f"  内容 {old_id}: creator_id={creator_id} 在app_user表中不存在")
            
            insert_sql = """
            INSERT INTO knowledge (id, name, description, parent_id, node_type, tags, created_by, created_time, updated_time, effective_end_time, status, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                new_id,
                safe_title or '',
                safe_text or '',
                parent_id,
                'doc',
                json.dumps(tags, ensure_ascii=False),
                created_by,
                created or datetime.now(),
                updated,
                expired,
                1,
                0
            )
            
            try:
                mysql_cursor.execute(insert_sql, values)
                self.id_mapping[f"content_{old_id}"] = new_id
                print(f"  创建内容: id={new_id}, title={safe_title[:30]}..., parent_id={parent_id}")
            except Exception as e:
                # 打印问题数据，便于定位
                preview = (safe_text or '')[:120]
                print(f"❗ 内容写入失败 id={old_id}, new_id={new_id}, error={e}")
                print(f"   title_len={len(safe_title or '')}, text_len={len(safe_text or '')}")
                print(f"   title_preview={repr((safe_title or '')[:80])}")
                print(f"   text_preview={repr(preview)}")
                # 继续抛出以便上层回滚或终止
                raise
            
        self.mysql_conn.commit()
        print(f"✅ 内容数据迁移完成: {len(contents)} 条记录")
    
    def migrate_uploads(self):
        """迁移文件上传数据"""
        print("\n🔄 开始迁移文件数据...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT id, file, created, content_item_id FROM app_upload")
        uploads = cursor.fetchall()
        
        mysql_cursor = self.mysql_conn.cursor()
        
        for upload in uploads:
            old_id, file_path, created, content_item_id = upload
            
            # 生成新的ID
            mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM attachments")
            new_id = mysql_cursor.fetchone()[0]
            
            # 获取关联的知识ID
            knowledge_id = None
            if content_item_id and f"content_{content_item_id}" in self.id_mapping:
                knowledge_id = self.id_mapping[f"content_{content_item_id}"]
            
            if not knowledge_id:
                continue  # 跳过没有关联内容的文件
            
            # 提取文件名和类型
            file_name = os.path.basename(file_path) if file_path else f"file_{old_id}"
            file_type = os.path.splitext(file_name)[1] if file_name else ''
            
            insert_sql = """
            INSERT INTO attachments (id, knowledge_id, file_name, file_path, file_size, file_type, upload_time, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                new_id,
                knowledge_id,
                file_name,
                file_path or '',
                0,  # 文件大小，需要实际计算
                file_type,
                created or datetime.now(),
                0
            )
            
            mysql_cursor.execute(insert_sql, values)
            
        self.mysql_conn.commit()
        print(f"✅ 文件数据迁移完成: {len(uploads)} 条记录")
    
    def migrate_feedbacks(self):
        """迁移反馈数据"""
        print("\n🔄 开始迁移反馈数据...")
        
        cursor = self.sqlite_conn.cursor()
        # 获取app_feedback表的数据，包括creator_id字段
        cursor.execute("SELECT id, text, created, content_item_id, creator_id FROM app_feedback")
        feedbacks = cursor.fetchall()
        
        mysql_cursor = self.mysql_conn.cursor()
        
        # 定义反馈类型映射（大小写不敏感）
        feedback_types = {
            'out of date': 'OUT_OF_DATE',
            'unclear': 'UNCLEAR',
            'incorrect': 'INCORRECT'
        }
        
        for feedback in feedbacks:
            old_id, text, created, content_item_id, creator_id = feedback
            
            # 生成新的ID
            mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM knowledge_feedbacks")
            new_id = mysql_cursor.fetchone()[0]
            
            # 获取关联的知识ID
            knowledge_id = None
            if content_item_id and f"content_{content_item_id}" in self.id_mapping:
                knowledge_id = self.id_mapping[f"content_{content_item_id}"]
            
            if not knowledge_id:
                continue
            
            # 判断反馈类型，大小写不敏感
            feedback_type = None
            feedback_content = text or ''
            
            # 检查是否为预定义的反馈类型
            for key, value in feedback_types.items():
                if feedback_content.lower().strip() == key.lower():
                    feedback_type = value
                    feedback_content = ''  # 如果是预定义类型，内容置空
                    break
            
            # 获取用户ID，使用creator_id关联app_user表的username
            new_user_id = 1  # 默认用户ID
            if creator_id:
                # 查询app_user表中对应的username
                creator_cursor = self.sqlite_conn.cursor()
                creator_cursor.execute("SELECT username FROM app_user WHERE id = ?", (creator_id,))
                creator_result = creator_cursor.fetchone()
                
                if creator_result and creator_result[0]:
                    username = creator_result[0]
                    # 在新表中查询对应的用户ID
                    mysql_cursor.execute("SELECT id FROM users WHERE staffid = %s", (username,))
                    user_result = mysql_cursor.fetchone()
                    if user_result:
                        new_user_id = user_result[0]
                        print(f"  反馈 {old_id}: 找到用户 {username}, 新ID={new_user_id}")
                    else:
                        print(f"  反馈 {old_id}: 用户 {username} 在新系统中不存在")
                else:
                    print(f"  反馈 {old_id}: creator_id={creator_id} 在app_user表中不存在")
            
            insert_sql = """
            INSERT INTO knowledge_feedbacks (id, knowledge_id, user_id, content, feedback_type, created_time, deleted)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                new_id,
                knowledge_id,
                new_user_id,
                feedback_content,
                feedback_type,  # 新增反馈类型字段
                created or datetime.now(),
                0
            )
            
            mysql_cursor.execute(insert_sql, values)
            
        self.mysql_conn.commit()
        print(f"✅ 反馈数据迁移完成: {len(feedbacks)} 条记录")
    
    def migrate_favorites(self):
        """迁移收藏数据"""
        print("\n🔄 开始迁移收藏数据...")
        
        cursor = self.sqlite_conn.cursor()
        cursor.execute("SELECT id, contentitem_id, user_id FROM app_contentitem_user_favourited")
        favorites = cursor.fetchall()
        
        mysql_cursor = self.mysql_conn.cursor()
        
        for favorite in favorites:
            old_id, content_item_id, user_id = favorite
            
            # 生成新的ID
            mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM knowledge_favorites")
            new_id = mysql_cursor.fetchone()[0]
            
            # 获取关联的知识ID
            knowledge_id = None
            if content_item_id and f"content_{content_item_id}" in self.id_mapping:
                knowledge_id = self.id_mapping[f"content_{content_item_id}"]
            
            if not knowledge_id:
                continue
            
            # 获取用户ID，使用user_id关联app_user表的username
            new_user_id = 1  # 默认用户ID
            if user_id:
                # 查询app_user表中对应的username
                user_cursor = self.sqlite_conn.cursor()
                user_cursor.execute("SELECT username FROM app_user WHERE id = ?", (user_id,))
                user_result = user_cursor.fetchone()
                
                if user_result and user_result[0]:
                    username = user_result[0]
                    # 在新表中查询对应的用户ID
                    mysql_cursor.execute("SELECT id FROM users WHERE staffid = %s", (username,))
                    user_result = mysql_cursor.fetchone()
                    if user_result:
                        new_user_id = user_result[0]
                        print(f"  收藏 {old_id}: 找到用户 {username}, 新ID={new_user_id}")
                    else:
                        print(f"  收藏 {old_id}: 用户 {username} 在新系统中不存在")
                else:
                    print(f"  收藏 {old_id}: user_id={user_id} 在app_user表中不存在")
            
            insert_sql = """
            INSERT INTO knowledge_favorites (id, knowledge_id, user_id, created_time, deleted)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                new_id,
                knowledge_id,
                new_user_id,
                datetime.now(),
                0
            )
            
            mysql_cursor.execute(insert_sql, values)
            
        self.mysql_conn.commit()
        print(f"✅ 收藏数据迁移完成: {len(favorites)} 条记录")
    
    def run_migration(self):
        """运行完整迁移"""
        print("🚀 开始历史系统数据迁移...")
        
        try:
            # 连接数据库
            self.connect_databases()
            # 确保目标库新增字段已就绪
            self.ensure_target_schema()
            
            # 按顺序迁移数据
            self.migrate_users()
            self.migrate_categories()
            self.migrate_content()
            self.migrate_uploads()
            self.migrate_feedbacks()
            self.migrate_favorites()
            self.migrate_search_history()
            
            print("\n✅ 数据迁移完成！")
            print(f"📊 ID映射关系已保存，共 {len(self.id_mapping)} 个映射")
            
        except Exception as e:
            print(f"❌ 迁移过程中出现错误: {e}")
            if self.mysql_conn:
                self.mysql_conn.rollback()
        finally:
            # 关闭连接
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.mysql_conn:
                self.mysql_conn.close()

def main():
    # 配置
    sqlite_db_path = input("请输入 SQLite 数据库文件路径: ").strip()
    if not os.path.exists(sqlite_db_path):
        print("❌ SQLite 数据库文件不存在！")
        return
    
    # 提示用户输入MySQL配置
    host = input("请输入MySQL主机地址 [localhost]: ").strip() or 'localhost'
    user = input("请输入MySQL用户名 [root]: ").strip() or 'root'
    password = input("请输入MySQL密码 [xmc131455]: ").strip() or 'xmc131455'
    database = input("请输入MySQL数据库名 [knowledge_base]: ").strip() or 'knowledge_base'
    
    mysql_config = {
        'host': host,
        'user': user,
        'password': password,
        'database': database
    }
    
    # 运行迁移
    migration = LegacyDataMigration(sqlite_db_path, mysql_config)
    migration.run_migration()

    def migrate_search_history(self):
        """迁移搜索历史数据"""
        print("\n🔄 开始迁移搜索历史数据...")
        
        # 首先获取所有用户的ID和username映射关系
        user_mapping = {}
        user_cursor = self.sqlite_conn.cursor()
        user_cursor.execute("SELECT id, username FROM app_user")
        user_results = user_cursor.fetchall()
        for user_id, username in user_results:
            user_mapping[user_id] = username
        print(f"  加载用户映射: {len(user_mapping)} 条记录")
        
        cursor = self.sqlite_conn.cursor()
        # 查询app_helpfulness表，只查询需要的字段
        cursor.execute("""
            SELECT 
                ah.id, 
                ah."query", 
                ah.created,
                ah.user_id
            FROM app_helpfulness ah
        """)
        search_histories = cursor.fetchall()
        
        mysql_cursor = self.mysql_conn.cursor()
        
        # 创建新用户ID映射缓存
        new_user_id_cache = {}
        
        for history in search_histories:
            old_id, query, created, user_id = history
            
            # 生成新的ID
            mysql_cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM search_history")
            new_id = mysql_cursor.fetchone()[0]
            
            # 使用缓存的用户映射获取新用户ID
            new_user_id = 1  # 默认用户ID
            
            # 如果用户ID已经在缓存中，直接使用
            if user_id in new_user_id_cache:
                new_user_id = new_user_id_cache[user_id]
            elif user_id in user_mapping:
                # 从用户映射中获取username
                username = user_mapping[user_id]
                # 在新表中查询对应的用户ID
                mysql_cursor.execute("SELECT id FROM users WHERE staffid = %s", (username,))
                user_result = mysql_cursor.fetchone()
                if user_result:
                    new_user_id = user_result[0]
                    # 将结果存入缓存
                    new_user_id_cache[user_id] = new_user_id
                    print(f"  搜索历史 {old_id}: 找到用户 {username}, 新ID={new_user_id}")
                else:
                    print(f"  搜索历史 {old_id}: 用户 {username} 在新系统中不存在")
            else:
                print(f"  搜索历史 {old_id}: user_id={user_id} 在用户映射中不存在")
            
            insert_sql = """
            INSERT INTO search_history (
                id, 
                query, 
                user_id, 
                search_time,
                created_time, 
                deleted
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (
                new_id,
                query or '',
                new_user_id,
                created or datetime.now(),
                created or datetime.now(),
                0
            )
            
            try:
                mysql_cursor.execute(insert_sql, values)
                print(f"  创建搜索历史: id={new_id}, query={query[:30] if query else ''}")
            except Exception as e:
                print(f"❗ 搜索历史写入失败 id={old_id}, new_id={new_id}, error={e}")
                raise
            
        self.mysql_conn.commit()
        print(f"✅ 搜索历史数据迁移完成: {len(search_histories)} 条记录")

if __name__ == "__main__":
    main()
