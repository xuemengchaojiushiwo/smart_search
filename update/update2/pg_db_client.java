#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL数据库客户端
用于连接PostgreSQL数据库并查询知识数据
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from typing import List, Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class PostgreSQLClient:
    """PostgreSQL数据库客户端"""
    
    def __init__(self):
        self.connection = None
        self._connect()
    
    def _connect(self):
        """连接数据库"""
        try:
            # PostgreSQL连接配置
            config = {
                'host': os.getenv('PG_HOST', 'localhost'),
                'port': int(os.getenv('PG_PORT', '5432')),
                'user': os.getenv('PG_USER', 'postgres'),
                'password': os.getenv('PG_PASSWORD', 'admin'),
                'database': os.getenv('PG_DATABASE', 'smart_search'),
                'client_encoding': 'utf8'
            }
            
            self.connection = psycopg2.connect(**config)
            logger.info(f"成功连接PostgreSQL数据库: {config['host']}:{config['port']}/{config['database']}")
            
        except Exception as e:
            logger.error(f"PostgreSQL数据库连接失败: {e}")
            self.connection = None
    
    def is_connected(self) -> bool:
        """检查数据库连接状态"""
        if self.connection is None:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except:
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询并返回结果"""
        if not self.is_connected():
            self._connect()
        
        if not self.is_connected():
            raise Exception("数据库连接失败")
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise
    
    def get_knowledge_data(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """获取指定知识ID的数据"""
        query = """
        SELECT 
            id,
            name,
            description,
            parent_id,
            node_type,
            tags,
            created_by,
            created_time,
            updated_time,
            effective_end_time,
            status,
            deleted
        FROM knowledge
        WHERE id = %s AND deleted = 0
        """
        
        try:
            results = self.execute_query(query, (knowledge_id,))
            return results[0] if results else None
        except Exception as e:
            logger.error(f"获取知识数据失败 (ID: {knowledge_id}): {e}")
            return None
    
    def get_attachments(self, knowledge_id: int) -> List[Dict[str, str]]:
        """获取指定知识ID的附件信息"""
        query = """
        SELECT 
            file_name,
            file_path,
            file_type,
            file_size
        FROM attachments
        WHERE knowledge_id = %s AND deleted = 0
        ORDER BY upload_time ASC
        """
        
        try:
            results = self.execute_query(query, (knowledge_id,))
            return results
        except Exception as e:
            logger.error(f"获取附件信息失败 (ID: {knowledge_id}): {e}")
            return []
    
    def check_es_exists(self, knowledge_id: int) -> bool:
        """检查ES中是否已存在该知识ID的文档"""
        # 这里可以添加ES查询逻辑
        # 暂时返回False，表示不存在
        return False
    
    def get_knowledge_ids(self, start_knowledge_id: int) -> List[int]:
        """获取需要处理的知识ID列表"""
        query = """
        SELECT id
        FROM knowledge
        WHERE id >= %s 
        AND node_type = 'doc'
        AND deleted = 0
        ORDER BY id
        """
        
        try:
            results = self.execute_query(query, (start_knowledge_id,))
            return [row['id'] for row in results]
        except Exception as e:
            logger.error(f"获取知识ID列表失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None


# 创建全局实例
pg_db_client = PostgreSQLClient()
