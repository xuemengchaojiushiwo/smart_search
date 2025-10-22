#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elasticsearch客户端模块
"""

import logging
import hashlib
from typing import List, Optional, Dict, Any
from langchain.schema import Document

try:
    from .config import ES_CONFIG, EMBEDDING_DIMS
    from .ai_client_manager import get_ai_manager
except ImportError:
    # 当直接运行时使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import ES_CONFIG, EMBEDDING_DIMS
    from ai_client_manager import get_ai_manager

logger = logging.getLogger(__name__)

# 初始化ES客户端
from elasticsearch import Elasticsearch

es_client = Elasticsearch(
    [f"http://{ES_CONFIG['host']}:{ES_CONFIG['port']}"],
    basic_auth=(ES_CONFIG['username'], ES_CONFIG['password']) if ES_CONFIG['username'] else None,
    verify_certs=ES_CONFIG['verify_certs']
)


def get_embedding(text: str) -> list:
    """获取文本嵌入向量，通过AI管理器调用"""
    try:
        logger.info(f"[DEBUG] 开始生成embedding, 文本长度: {len(text)}")
        
        # 获取AI管理器
        manager = get_ai_manager()
        
        # 调用管理器的get_embeddings方法
        result = manager.get_embeddings([text])
        
        # 检查结果
        if "error" in result:
            logger.error(f"[DEBUG] embedding生成失败: {result['error']}")
            return None
        
        # 提取embedding
        if "data" in result and len(result["data"]) > 0:
            embedding = result["data"][0].get("embedding")
            if embedding:
                logger.info(f"[DEBUG] embedding生成成功: 维度={len(embedding)}, 前5个值={embedding[:5]}, 使用API: {manager.get_current_api()}")
                return embedding
        
        logger.error(f"[DEBUG] 无法从结果中提取embedding: {result}")
        return None
    except Exception as e:
        logger.error(f"[DEBUG] embedding生成异常: {e}")
        return None


def store_chunks_to_es(chunks: List[Document], knowledge_id: int, workspaces: Optional[List[str]] = None):
    """
    将chunks存储到Elasticsearch
    """
    stored_count = 0
    
    # 1. 先存储知识元数据块（用于搜索和匹配）
    if chunks:
        first_chunk = chunks[0]
        metadata = first_chunk.metadata
        
        # 构建元数据文本，用于embedding
        metadata_text_parts = []
        
        knowledge_name = metadata.get("knowledge_name", "")
        if knowledge_name:
            metadata_text_parts.append(f"知识名称：{knowledge_name}")
        
        description = metadata.get("description", "")
        if description:
            # 移除HTML标签
            import re
            clean_desc = re.sub(r'<[^>]+>', '', description)
            if clean_desc.strip():
                metadata_text_parts.append(f"描述：{clean_desc}")
        
        tags = metadata.get("tags", "")
        if tags:
            if isinstance(tags, list):
                tags_str = "、".join(tags)
            else:
                tags_str = tags
            if tags_str.strip():
                metadata_text_parts.append(f"标签：{tags_str}")
        
        effective_time = metadata.get("effective_time", "")
        if effective_time:
            metadata_text_parts.append(f"生效时间：{effective_time}")
        
        source_file = metadata.get("source_file", "")
        if source_file:
            metadata_text_parts.append(f"文件名：{source_file}")
        
        # 合并元数据文本
        metadata_text = "\n".join(metadata_text_parts)
        
        if metadata_text.strip():
            try:
                # 为元数据生成embedding
                metadata_embedding = get_embedding(metadata_text)
                
                if metadata_embedding:
                    # 生成元数据块ID
                    metadata_doc_id = hashlib.md5(f"{knowledge_id}_metadata".encode()).hexdigest()
                    
                    # 构建元数据ES文档
                    metadata_es_doc = {
                        "content": metadata_text,
                        "embedding": metadata_embedding,
                        "knowledge_id": knowledge_id,
                        "knowledge_name": knowledge_name,
                        "description": description,
                        "tags": tags,
                        "effective_time": effective_time,
                        "source_file": source_file,
                        "chunk_index": -1,  # 使用-1标识这是元数据块
                        "chunk_type": "metadata",  # 标识为元数据类型
                        "page_num": 0,
                        "bbox": [],
                        "positions": [],
                        "mini_chunks": [],
                        "node_type": "metadata",
                        "weight": 1.5  # 元数据块权重稍高
                    }
                    
                    # 添加工作空间信息
                    if workspaces:
                        metadata_es_doc["workspaces"] = workspaces
                    
                    # 存储元数据块到ES
                    es_client.index(index=ES_CONFIG['index'], id=metadata_doc_id, document=metadata_es_doc)
                    stored_count += 1
                    logger.info(f"已存储知识元数据块: knowledge_id={knowledge_id}, 文本长度={len(metadata_text)}")
                else:
                    logger.warning(f"知识元数据块embedding生成失败: knowledge_id={knowledge_id}")
            except Exception as e:
                logger.error(f"存储知识元数据块失败: {e}")
    
    # 2. 存储内容块
    for i, chunk in enumerate(chunks):
        try:
            # 生成文档ID
            doc_id = hashlib.md5(f"{knowledge_id}_{i}_{chunk.page_content[:100]}".encode()).hexdigest()
            
            # 为chunk生成embedding
            # 检查文本长度并截断，避免超过512 tokens的限制
            MAX_TEXT_LENGTH = 1500  # 安全阈值，避免超过512 tokens
            chunk_text = chunk.page_content
            if len(chunk_text) > MAX_TEXT_LENGTH:
                logger.warning(f"Chunk {i} 文本长度({len(chunk_text)})超过限制({MAX_TEXT_LENGTH})，将进行截断")
                # 对于长文本，取开头和结尾的部分
                head_length = MAX_TEXT_LENGTH // 2
                tail_length = MAX_TEXT_LENGTH // 2
                truncated_text = chunk_text[:head_length] + "..." + chunk_text[-tail_length:]
                logger.info(f"截断后长度: {len(truncated_text)}")
                chunk_text = truncated_text
            else:
                chunk_text = chunk.page_content
                
            chunk_embedding = get_embedding(chunk_text)
            if not chunk_embedding:
                logger.warning(f"Chunk {i} embedding生成失败，跳过")
                continue
            # 校验 embedding 维度与配置一致（自定义API切换成1024时避免落错索引）
            try:
                emb_len = len(chunk_embedding) if chunk_embedding is not None else 0
            except Exception:
                emb_len = 0
            if emb_len != EMBEDDING_DIMS:
                logger.error(f"Chunk {i} embedding 维度不匹配: got={emb_len}, expected={EMBEDDING_DIMS}，已跳过入库")
                continue
            
            # 准备ES文档，确保中文内容使用正确的UTF-8编码
            es_doc = {
                "content": chunk.page_content,
                "embedding": chunk_embedding,
                "knowledge_id": chunk.metadata.get("knowledge_id", knowledge_id),
                "knowledge_name": chunk.metadata.get("knowledge_name", ""),
                "description": chunk.metadata.get("description", ""),
                "tags": chunk.metadata.get("tags", ""),
                "effective_time": chunk.metadata.get("effective_time", ""),
                "source_file": chunk.metadata.get("source_file", ""),
                "chunk_index": chunk.metadata.get("chunk_index", i),
                "chunk_type": chunk.metadata.get("chunk_type", "content"),
                "page_num": chunk.metadata.get("page_num", 1),
                "bbox": chunk.metadata.get("bbox", []),
                "positions": chunk.metadata.get("positions", []),
                "mini_chunks": chunk.metadata.get("mini_chunks", []),
                "node_type": "doc",  # 明确标识这是文档类型
                "weight": 1.0
            }
            
            # 添加工作空间信息
            if workspaces:
                es_doc["workspaces"] = workspaces
            
            # 确保所有字符串字段使用正确的UTF-8编码
            for key, value in es_doc.items():
                if isinstance(value, str):
                    # 确保字符串是有效的UTF-8编码
                    es_doc[key] = value.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            
            # 存储到ES
            es_client.index(index=ES_CONFIG['index'], id=doc_id, document=es_doc)
            stored_count += 1
            
            if (i + 1) % 10 == 0:
                logger.info(f"已存储 {i + 1}/{len(chunks)} 个chunks")
                
        except Exception as e:
            logger.error(f"存储chunk {i} 失败: {e}")
            continue

    logger.info(f"ES存储完成，成功存储 {stored_count}/{len(chunks)} 个chunks")
    return stored_count


def search_es_chunks(query_embedding: list, filters: List[Dict] = None, size: int = 10) -> List[Dict]:
    """
    在ES中搜索相关的chunks
    """
    if filters is None:
        filters = []
    
    search_query = {
        "size": size,
        "query": {
            "script_score": {
                "query": {
                    "bool": {
                        "filter": filters
                    }
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        },
        "_source": [
            "content",
            "knowledge_id",
            "knowledge_name",
            "description",
            "tags",
            "effective_time",
            "source_file",
            "page_num",
            "chunk_index",
            "bbox",
            "positions",
            "mini_chunks"
        ]
    }
    
    try:
        search_response = es_client.search(index=ES_CONFIG['index'], body=search_query)
        hits = search_response.get('hits', {}).get('hits', [])
        
        results = []
        for hit in hits:
            results.append({
                'source': hit['_source'],
                'score': hit['_score']
            })
        
        return results
    except Exception as e:
        logger.error(f"ES搜索失败: {e}")
        return []


def store_knowledge_metadata_to_es(metadata: Dict[str, Any]) -> bool:
    """
    为没有附件的知识生成元数据embedding并存储到ES
    
    Args:
        metadata: 知识元数据字典，包含knowledge_id, knowledge_name, description等
        
    Returns:
        bool: 是否存储成功
    """
    try:
        knowledge_id = metadata.get("knowledge_id")
        knowledge_name = metadata.get("knowledge_name", "")
        description = metadata.get("description", "")
        tags = metadata.get("tags", [])
        effective_time = metadata.get("effective_time", "")
        source_file = metadata.get("source_file", "")
        workspaces = metadata.get("workspaces", [])
        
        if not knowledge_id:
            logger.error("知识ID不能为空")
            return False
        
        # 构建元数据文本
        metadata_text_parts = []
        
        if knowledge_name:
            metadata_text_parts.append(f"知识名称：{knowledge_name}")
        
        if description:
            metadata_text_parts.append(f"知识描述：{description}")
        
        if tags:
            if isinstance(tags, list):
                tags_str = "、".join(tags)
            else:
                tags_str = str(tags)
            metadata_text_parts.append(f"标签：{tags_str}")
        
        if effective_time:
            metadata_text_parts.append(f"生效时间：{effective_time}")
        
        if source_file:
            metadata_text_parts.append(f"文件名：{source_file}")
        
        # 合并元数据文本
        metadata_text = "\n".join(metadata_text_parts)
        
        if not metadata_text.strip():
            logger.warning(f"知识元数据为空，跳过存储: knowledge_id={knowledge_id}")
            return False
        
        # 为元数据生成embedding
        metadata_embedding = get_embedding(metadata_text)
        
        if not metadata_embedding:
            logger.warning(f"知识元数据块embedding生成失败: knowledge_id={knowledge_id}")
            return False
        
        # 校验embedding维度
        try:
            emb_len = len(metadata_embedding) if metadata_embedding is not None else 0
        except Exception:
            emb_len = 0
        if emb_len != EMBEDDING_DIMS:
            logger.error(f"知识元数据块embedding维度不匹配: got={emb_len}, expected={EMBEDDING_DIMS}")
            return False
        
        # 生成元数据块ID
        metadata_doc_id = hashlib.md5(f"{knowledge_id}_metadata".encode()).hexdigest()
        
        # 构建元数据ES文档
        metadata_es_doc = {
            "content": metadata_text,
            "embedding": metadata_embedding,
            "knowledge_id": knowledge_id,
            "knowledge_name": knowledge_name,
            "description": description,
            "tags": tags,
            "effective_time": effective_time,
            "source_file": source_file,
            "chunk_index": -1,  # 使用-1标识这是元数据块
            "chunk_type": "metadata",  # 标识为元数据类型
            "page_num": 0,
            "bbox": [],
            "positions": [],
            "mini_chunks": [],
            "node_type": "metadata",
            "weight": 1.5  # 元数据块权重稍高
        }
        
        # 添加工作空间信息
        if workspaces:
            metadata_es_doc["workspaces"] = workspaces
        
        # 存储元数据块到ES
        es_client.index(index=ES_CONFIG['index'], id=metadata_doc_id, document=metadata_es_doc)
        
        logger.info(f"已存储知识元数据块: knowledge_id={knowledge_id}, 文本长度={len(metadata_text)}")
        return True
        
    except Exception as e:
        logger.error(f"存储知识元数据块失败: {e}")
        return False