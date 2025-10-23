#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文档嵌入服务
用于处理历史数据的文档嵌入操作
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import threading
import time

# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import BatchEmbeddingRequest, BatchEmbeddingResponse, BatchEmbeddingStatus
from document_processor import process_document_unified
from es_client import store_chunks_to_es
from config import UPLOAD_DIR
from pg_db_client import pg_db_client as db_client

logger = logging.getLogger(__name__)


class BatchEmbeddingService:
    """批量文档嵌入服务"""
    
    def __init__(self):
        self.is_running = False
        self.processed_count = 0
        self.total_count = 0
        self.current_knowledge_id = None
        self.start_time = None
        self.last_update_time = None
        self.errors = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
    
    def get_status(self) -> BatchEmbeddingStatus:
        """获取当前处理状态"""
        with self._lock:
            return BatchEmbeddingStatus(
                is_running=self.is_running,
                processed_count=self.processed_count,
                total_count=self.total_count,
                current_knowledge_id=self.current_knowledge_id,
                start_time=self.start_time.isoformat() if self.start_time else None,
                last_update_time=self.last_update_time.isoformat() if self.last_update_time else None,
                errors=self.errors.copy()
            )
    
    def stop_processing(self):
        """停止处理"""
        self._stop_event.set()
        logger.info("批量处理已停止")
    
    def reset_status(self):
        """重置状态"""
        with self._lock:
            self.is_running = False
            self.processed_count = 0
            self.total_count = 0
            self.current_knowledge_id = None
            self.start_time = None
            self.last_update_time = None
            self.errors = []
            self._stop_event.clear()
    
    def _update_status(self, processed_count: int, current_knowledge_id: Optional[int] = None):
        """更新处理状态"""
        with self._lock:
            self.processed_count = processed_count
            self.current_knowledge_id = current_knowledge_id
            self.last_update_time = datetime.now()
    
    def _add_error(self, knowledge_id: int, error: str, details: str = ""):
        """添加错误记录"""
        with self._lock:
            self.errors.append({
                "knowledge_id": knowledge_id,
                "error": error,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
    
    def _get_knowledge_data_from_db(self, knowledge_id: int) -> Optional[Dict[str, Any]]:
        """从数据库获取知识数据"""
        try:
            return db_client.get_knowledge_data(knowledge_id)
        except Exception as e:
            logger.error(f"从数据库获取知识数据失败 (ID: {knowledge_id}): {e}")
            return None
    
    def _get_attachment_files(self, knowledge_id: int, file_base_path: str) -> List[Dict[str, str]]:
        """获取知识ID对应的附件文件列表"""
        try:
            # 先从数据库获取附件信息
            attachments = db_client.get_attachments(knowledge_id)
            files = []
            
            for attachment in attachments:
                file_name = attachment.get('file_name', '')
                file_path = attachment.get('file_path', '')
                file_type = attachment.get('file_type', '')
                
                # 处理文件路径：支持相对路径和绝对路径
                if file_path:
                    if os.path.isabs(file_path):
                        # 绝对路径，直接使用
                        full_path = file_path
                        logger.info(f"使用绝对路径: {full_path}")
                    else:
                        # 相对路径，需要拼接基础路径
                        if file_path.startswith('uploads/'):
                            # 去掉uploads/前缀，然后拼接基础路径
                            relative_path = file_path[8:]  # 去掉"uploads/"
                            # 检查是否按知识ID分目录存储
                            knowledge_file_path = os.path.join(file_base_path, str(knowledge_id), relative_path)
                            if os.path.exists(knowledge_file_path):
                                full_path = knowledge_file_path
                            else:
                                # 如果分目录不存在，尝试直接在uploads目录下查找
                                full_path = os.path.join(file_base_path, relative_path)
                        else:
                            full_path = os.path.join(file_base_path, file_path)
                else:
                    # 如果没有file_path，尝试使用文件名在uploads目录下查找
                    full_path = os.path.join(file_base_path, file_name)
                
                # 检查文件是否存在
                if os.path.exists(full_path):
                    # 检查文件类型
                    ext = Path(file_name).suffix.lower()
                    chunkable_extensions = {
                        ".pdf", ".docx", ".doc", ".xlsx", ".xls", 
                        ".pptx", ".ppt", ".txt", ".hwp", ".hwpx"
                    }
                    
                    if ext in chunkable_extensions:
                        files.append({
                            "filename": file_name,
                            "file_path": full_path,
                            "file_type": ext
                        })
                else:
                    logger.warning(f"附件文件不存在: {full_path}")
            
            # 如果数据库中没有附件信息，尝试从文件系统扫描
            if not files:
                knowledge_dir = os.path.join(file_base_path, str(knowledge_id))
                if os.path.exists(knowledge_dir):
                    for filename in os.listdir(knowledge_dir):
                        file_path = os.path.join(knowledge_dir, filename)
                        if os.path.isfile(file_path):
                            ext = Path(filename).suffix.lower()
                            chunkable_extensions = {
                                ".pdf", ".docx", ".doc", ".xlsx", ".xls", 
                                ".pptx", ".ppt", ".txt", ".hwp", ".hwpx"
                            }
                            
                            if ext in chunkable_extensions:
                                files.append({
                                    "filename": filename,
                                    "file_path": file_path,
                                    "file_type": ext
                                })
            
            return files
            
        except Exception as e:
            logger.error(f"获取附件文件失败 (ID: {knowledge_id}): {e}")
            return []
    
    def _check_es_exists(self, knowledge_id: int) -> bool:
        """检查ES中是否已存在该知识ID的文档"""
        try:
            return db_client.check_es_exists(knowledge_id)
        except Exception as e:
            logger.warning(f"检查ES存在性失败: {e}")
            return False
    
    def _process_single_document(self, knowledge_id: int, file_info: Dict[str, str], 
                                knowledge_data: Dict[str, Any], force_reprocess: bool = False) -> bool:
        """
        处理单个文档
        """
        try:
            # 检查是否需要跳过（如果已存在且不强制重新处理）
            if not force_reprocess and self._check_es_exists(knowledge_id):
                logger.info(f"知识ID {knowledge_id} 的文档已存在，跳过处理")
                return True
            
            file_path = file_info["file_path"]
            filename = file_info["filename"]
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                error_msg = f"文件不存在: {file_path}"
                logger.error(error_msg)
                self._add_error(knowledge_id, "文件不存在", file_path)
                return False
            
            logger.info(f"开始处理文档: {filename} (知识ID: {knowledge_id})")
            
            # 使用现有的文档处理逻辑
            result = process_document_unified(
                file_path=file_path,
                filename=filename,
                knowledge_id=knowledge_id,
                knowledge_name=knowledge_data.get("name", ""),
                description=knowledge_data.get("description", ""),
                tags=json.dumps(knowledge_data.get("tags", []), ensure_ascii=False),
                effective_time=knowledge_data.get("effective_time", ""),
                workspaces=json.dumps(knowledge_data.get("workspaces", []), ensure_ascii=False)
            )
            
            logger.info(f"文档处理完成: {filename}, 生成 {result['chunks_count']} 个chunks")
            return True
            
        except Exception as e:
            error_msg = f"处理文档失败: {str(e)}"
            logger.error(error_msg)
            self._add_error(knowledge_id, "处理失败", error_msg)
            return False
    
    def _get_knowledge_ids_from_db(self, start_knowledge_id: Optional[int] = None) -> List[int]:
        """从数据库获取需要处理的知识ID列表"""
        try:
            return db_client.get_knowledge_ids(start_knowledge_id)
        except Exception as e:
            logger.error(f"获取知识ID列表失败: {e}")
            return []
    
    async def _get_knowledge_files_from_java(self, request: BatchEmbeddingRequest) -> List[Dict[str, Any]]:
        """从Java查询知识和文件信息"""
        try:
            # 这里应该调用Java的API来获取知识和文件信息
            # 暂时使用数据库查询作为示例，实际应该调用Java服务
            knowledge_ids = self._get_knowledge_ids_from_db(request.start_knowledge_id)
            
            knowledge_files_data = []
            for knowledge_id in knowledge_ids:
                # 获取知识基本信息
                knowledge_data = self._get_knowledge_data_from_db(knowledge_id)
                if not knowledge_data:
                    continue
                
                # 获取该知识的所有附件文件
                files = self._get_attachment_files(knowledge_id, "uploads")
                if not files:
                    # 如果没有文件，仍然需要处理元数据embedding
                    knowledge_files_data.append({
                        'knowledge_id': knowledge_id,
                        'knowledge_data': knowledge_data,
                        'files': []
                    })
                else:
                    # 有文件的情况
                    knowledge_files_data.append({
                        'knowledge_id': knowledge_id,
                        'knowledge_data': knowledge_data,
                        'files': files
                    })
            
            return knowledge_files_data
            
        except Exception as e:
            logger.error(f"从Java查询知识文件信息失败: {e}")
            return []
    
    async def _process_single_knowledge_embedding_only(self, knowledge_data: Dict[str, Any], 
                                                     request: BatchEmbeddingRequest) -> bool:
        """只处理embedding部分，不处理文件上传等"""
        try:
            knowledge_id = knowledge_data['knowledge_id']
            knowledge_info = knowledge_data['knowledge_data']
            files = knowledge_data['files']
            
            # 检查是否需要跳过（如果已存在且不强制重新处理）
            if not request.force_reprocess and self._check_es_exists(knowledge_id):
                logger.info(f"知识ID {knowledge_id} 的embedding已存在，跳过处理")
                return True
            
            success_count = 0
            total_files = len(files)
            
            # 处理文件embedding
            for file_info in files:
                try:
                    file_path = file_info["file_path"]
                    filename = file_info["filename"]
                    
                    # 检查文件是否存在
                    if not os.path.exists(file_path):
                        logger.warning(f"文件不存在，跳过: {file_path}")
                        continue
                    
                    logger.info(f"开始处理文件embedding: {filename} (知识ID: {knowledge_id})")
                    
                    # 使用现有的文档处理逻辑生成embedding
                    result = process_document_unified(
                        file_path=file_path,
                        filename=filename,
                        knowledge_id=knowledge_id,
                        knowledge_name=knowledge_info.get("name", ""),
                        description=knowledge_info.get("description", ""),
                        tags=json.dumps(knowledge_info.get("tags", []), ensure_ascii=False),
                        effective_time=knowledge_info.get("effective_time", ""),
                        workspaces=json.dumps(knowledge_info.get("workspaces", []), ensure_ascii=False)
                    )
                    
                    if result and result.get('chunks_count', 0) > 0:
                        success_count += 1
                        logger.info(f"文件 {filename} embedding处理成功，生成 {result['chunks_count']} 个chunks")
                    else:
                        logger.warning(f"文件 {filename} embedding处理失败")
                        
                except Exception as e:
                    logger.error(f"处理文件 {file_info.get('filename', 'unknown')} 时发生错误: {e}")
                    continue
            
            # 如果没有文件，处理元数据embedding
            if total_files == 0:
                logger.info(f"知识ID {knowledge_id} 没有文件，处理元数据embedding")
                try:
                    from es_client import store_knowledge_metadata_to_es
                    
                    metadata = {
                        "knowledge_id": knowledge_id,
                        "knowledge_name": knowledge_info.get("name", ""),
                        "description": knowledge_info.get("description", ""),
                        "tags": knowledge_info.get("tags", []),
                        "effective_time": knowledge_info.get("effective_time", ""),
                        "source_file": "",
                        "workspaces": knowledge_info.get("workspaces", [])
                    }
                    
                    success = store_knowledge_metadata_to_es(metadata)
                    if success:
                        success_count = 1  # 元数据embedding也算一个成功
                        logger.info(f"知识ID {knowledge_id} 元数据embedding处理成功")
                    else:
                        logger.warning(f"知识ID {knowledge_id} 元数据embedding处理失败")
                        
                except Exception as e:
                    logger.error(f"处理知识ID {knowledge_id} 元数据embedding时发生错误: {e}")
            
            # 至少有一个文件或元数据处理成功才算成功
            return success_count > 0
            
        except Exception as e:
            logger.error(f"处理知识ID {knowledge_data['knowledge_id']} embedding时发生异常: {e}")
            return False
    
    async def process_batch_embedding(self, request: BatchEmbeddingRequest) -> BatchEmbeddingResponse:
        """
        执行批量文档嵌入处理 - 从Java查询数据，只处理embedding部分
        """
        try:
            # 重置状态
            self.reset_status()
            
            # 从Java查询需要处理的知识和文件信息
            knowledge_files_data = await self._get_knowledge_files_from_java(request)
            if not knowledge_files_data:
                return BatchEmbeddingResponse(
                    success=True,
                    message="没有找到需要处理的知识和文件",
                    processed_count=0,
                    total_count=0
                )
            
            # 更新状态
            with self._lock:
                self.is_running = True
                self.total_count = len(knowledge_files_data)
                self.start_time = datetime.now()
            
            logger.info(f"开始批量embedding处理，共 {len(knowledge_files_data)} 个知识")
            
            processed_count = 0
            next_knowledge_id = None
            
            # 分批处理
            for i in range(0, len(knowledge_files_data), request.batch_size):
                if self._stop_event.is_set():
                    logger.info("处理被停止")
                    break
                
                batch_data = knowledge_files_data[i:i + request.batch_size]
                batch_knowledge_ids = [item['knowledge_id'] for item in batch_data]
                logger.info(f"处理批次 {i//request.batch_size + 1}: 知识ID {batch_knowledge_ids}")
                
                for knowledge_data in batch_data:
                    if self._stop_event.is_set():
                        break
                    
                    try:
                        knowledge_id = knowledge_data['knowledge_id']
                        
                        # 只处理embedding部分
                        success = await self._process_single_knowledge_embedding_only(
                            knowledge_data, 
                            request
                        )
                        
                        if success:
                            processed_count += 1
                            self._update_status(processed_count, knowledge_id)
                            logger.info(f"知识ID {knowledge_id} embedding处理成功 ({processed_count}/{self.total_count})")
                        else:
                            logger.warning(f"知识ID {knowledge_id} embedding处理失败")
                            self._add_error(knowledge_id, "embedding处理失败", "文档处理或嵌入存储失败")
                        
                        # 记录进度
                        if processed_count % 10 == 0:
                            logger.info(f"已处理 {processed_count}/{self.total_count} 个知识")
                    
                    except Exception as e:
                        error_msg = f"处理知识ID {knowledge_data['knowledge_id']} 时发生错误: {str(e)}"
                        logger.error(error_msg)
                        self._add_error(knowledge_data['knowledge_id'], "处理异常", error_msg)
                
                # 批次间暂停，避免资源占用过高
                if i + request.batch_size < len(knowledge_files_data) and not self._stop_event.is_set():
                    await asyncio.sleep(1)
            
            # 确定下一个知识ID
            if processed_count < self.total_count:
                remaining_data = knowledge_files_data[processed_count:]
                next_knowledge_id = remaining_data[0]['knowledge_id'] if remaining_data else None
            
            # 更新最终状态
            with self._lock:
                self.is_running = False
                self.last_update_time = datetime.now()
            
            success = processed_count > 0
            message = f"批量embedding处理完成，成功处理 {processed_count}/{self.total_count} 个知识"
            if self.errors:
                message += f"，失败 {len(self.errors)} 个"
            
            return BatchEmbeddingResponse(
                success=success,
                message=message,
                processed_count=processed_count,
                total_count=self.total_count,
                current_knowledge_id=self.current_knowledge_id,
                next_knowledge_id=next_knowledge_id,
                errors=self.errors.copy()
            )
            
        except Exception as e:
            error_msg = f"批量embedding处理失败: {str(e)}"
            logger.error(error_msg)
            
            with self._lock:
                self.is_running = False
                self.last_update_time = datetime.now()
            
            return BatchEmbeddingResponse(
                success=False,
                message=error_msg,
                processed_count=self.processed_count,
                total_count=self.total_count,
                errors=self.errors.copy()
            )


# 全局服务实例
batch_embedding_service = BatchEmbeddingService()
