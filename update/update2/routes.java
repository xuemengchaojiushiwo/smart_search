#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由模块
"""

import logging
import os
import tempfile
import requests
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup

# 使用绝对导入
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from models import (
    LdapValidateRequest, LdapValidateResponse, ChatRequest, ChatResponse,
    DocumentProcessRequest, DocumentProcessResponse,
    BatchEmbeddingRequest, BatchEmbeddingResponse, BatchEmbeddingStatus
)
from document_processor import process_document_unified
from rag_engine import chat_with_rag
from es_client import get_embedding
from batch_embedding_service import batch_embedding_service

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()


@router.get("/")
def read_root():
    """根路径"""
    return {
        "message": "智能知识库系统",
        "version": "2.0.0",
        "features": [
            "PyMuPDF Pro 文档处理",
            "PyMuPDF4LLM 结构化分块", 
            "LangChain 向量化",
            "Elasticsearch 存储",
            "极客智坊API 智能问答"
        ]
    }


@router.post("/api/ldap/validate", response_model=LdapValidateResponse)
def validate_ldap_user(request: LdapValidateRequest):
    """LDAP用户验证（模拟实现）"""
    logger.info(f"LDAP验证请求: {request.username}")
    
    # 模拟LDAP验证
    if request.username == "admin" and request.password == "password":
        return LdapValidateResponse(
            success=True,
            message="验证成功",
            email="admin@example.com",
            role="admin"
        )
    else:
        return LdapValidateResponse(
            success=False,
            message="用户名或密码错误"
        )


@router.post("/ldap/verify")
def ldap_verify(request: LdapValidateRequest):
    """LDAP验证接口，供Java调用"""
    username = request.username.strip()
    password = request.password
    
    # 模拟验证（可以后续集成真实LDAP）
    if not username or not password:
        raise HTTPException(status_code=401, detail="用户名或密码不能为空")
    
    # 模拟用户信息
    user_info = {
        "username": username,
        "email": f"{username}@example.com",
        "display_name": username.capitalize(),
        "role": "USER",
        "system_role": "Blocker",
    }
    
    return {
        "ok": True,
        "source": "mock",
        "user": user_info,
        "raw": {}
    }


@router.post("/api/document/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    knowledge_id: int = Form(None),
    knowledge_name: str = Form(None),
    description: str = Form(None),
    tags: str = Form(None),
    effective_time: str = Form(None),
    workspaces: str = Form(None)
):
    """
    处理上传的文档
    - 支持切分的格式：PDF、Word、Excel、PowerPoint、TXT 等
    - 不支持切分的格式：图片、音频、视频等（仅存储）
    """
    logger.info(f"开始处理文档: {file.filename}, 知识ID: {knowledge_id}")
    
    try:
        # 检查文件类型
        file_extension = Path(file.filename).suffix.lower()
        
        # 支持切分的文件类型
        chunkable_extensions = {
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", 
            ".pptx", ".ppt", ".txt", ".hwp", ".hwpx"
        }
        
        # 支持存储但不切分的文件类型（图片、音频、视频等）
        storage_only_extensions = {
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp",  # 图片
            ".mp3", ".wav", ".flac", ".aac", ".ogg",  # 音频
            ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv",  # 视频
            ".zip", ".rar", ".7z", ".tar", ".gz",  # 压缩包
            ".exe", ".msi", ".dmg", ".deb", ".rpm",  # 可执行文件
        }
        
        # 检查是否为支持的文件类型
        if file_extension not in chunkable_extensions and file_extension not in storage_only_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_extension}")
        
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 判断是否需要切分处理
            if file_extension in chunkable_extensions:
                # 进行文档切分处理
                result = process_document_unified(
                    temp_file_path,
                    file.filename,
                    knowledge_id,
                    knowledge_name=knowledge_name,
                    description=description,
                    tags=tags,
                    effective_time=effective_time,
                    workspaces=workspaces,
                )
                
                return DocumentProcessResponse(
                    success=True,
                    message=f"文档处理成功: {file.filename}",
                    chunks_count=result["chunks_count"],
                    knowledge_id=int(knowledge_id) if knowledge_id is not None else 0
                )
            else:
                # 仅存储，不进行切分处理
                logger.info(f"文件类型 {file_extension} 不支持切分，仅进行存储: {file.filename}")
                
                return DocumentProcessResponse(
                    success=True,
                    message=f"文件存储成功: {file.filename}（该文件类型不支持内容切分）",
                    chunks_count=0,
                    knowledge_id=int(knowledge_id) if knowledge_id is not None else 0
                )
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@router.post("/api/rag/chat", response_model=ChatResponse)
def chat_with_rag_endpoint(request: ChatRequest):
    """
    基于知识库的智能问答
    """
    return chat_with_rag(
        question=request.question,
        user_id=request.user_id,
        source_file=request.source_file,
        workspace=request.workspace
    )


@router.post("/api/embedding")
def get_text_embedding(request: dict):
    """
    获取文本的embedding向量
    """
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="文本不能为空")
        
        # 生成embedding
        embedding = get_embedding(text)
        
        if embedding:
            return {
                "success": True,
                "embedding": embedding,
                "dimension": len(embedding)
            }
        else:
            raise HTTPException(status_code=500, detail="生成embedding失败")
            
    except Exception as e:
        logger.error(f"获取embedding失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取embedding失败: {str(e)}")


@router.get("/api/health")
def health_check():
    """
    健康检查
    """
    try:
        # 检查ES连接
        from es_client import es_client
        es_info = es_client.info()
        
        # 检查PyMuPDF可用性
        try:
            import fitz
            pymupdf_status = "available"
        except ImportError:
            pymupdf_status = "unavailable"
        
        # 检查极客智坊API
        try:
            # 使用AI管理器获取授权信息
            from ai_client_manager import get_ai_manager
            manager = get_ai_manager()
            headers = {"Authorization": f"Bearer {manager.get_api_info().get('current_api')}"}
            response = requests.get("https://geekai.co/api/v1/models", headers=headers, timeout=5)
            geekai_status = "available" if response.status_code == 200 else "unavailable"
        except:
            geekai_status = "unavailable"
        
        return {
            "status": "healthy",
            "elasticsearch": "connected",
            "pymupdf": pymupdf_status,
            "geekai_api": geekai_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")


@router.post("/api/diff/summary")
def generate_diff_summary(request: Dict[str, Any]):
    """
    生成两个HTML版本之间的差异总结
    """
    try:
        # 直接导入本地模块
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from diff_summary import generate_diff_summary
        
        old_html = request.get("oldHtml", "")
        new_html = request.get("newHtml", "")
        
        if not old_html and not new_html:
            return {"success": True, "summary": "两个版本都为空，无变更。"}
        
        # 尝试使用AI生成总结
        try:
            summary = generate_diff_summary(old_html, new_html)
            if summary and not summary.startswith("无法生成") and not summary.startswith("生成差异总结时发生错误"):
                return {
                    "success": True,
                    "summary": summary
                }
        except Exception as inner_e:
            logger.error(f"调用AI生成差异总结失败: {inner_e}")
        
        # 如果AI生成失败，使用规则生成简单总结
        old_text = BeautifulSoup(old_html, 'html.parser').get_text(separator=' ', strip=True) if old_html else ""
        new_text = BeautifulSoup(new_html, 'html.parser').get_text(separator=' ', strip=True) if new_html else ""
        
        if not old_text:
            summary = "本次更新：首次添加内容。"
        elif not new_text:
            summary = "本次更新：删除了所有内容。"
        elif old_text == new_text:
            summary = "本次更新：内容未发生实质变化，可能调整了格式。"
        else:
            # 简单比较字符数量
            old_len = len(old_text)
            new_len = len(new_text)
            diff = new_len - old_len
            
            if diff > 0:
                summary = f"本次更新：内容有所增加，新增了约{diff}个字符。"
            elif diff < 0:
                summary = f"本次更新：内容有所减少，删除了约{abs(diff)}个字符。"
            else:
                summary = "本次更新：内容有所调整，但总字符数保持不变。"
        
        return {
            "success": True,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"生成差异总结失败: {e}")
        return {
            "success": False,
            "summary": "生成差异总结时发生错误，请查看HTML对比结果。",
            "error": str(e)
        }


@router.post("/api/batch/embedding/start", response_model=BatchEmbeddingResponse)
async def start_batch_embedding(request: BatchEmbeddingRequest):
    """
    启动批量文档嵌入处理
    - 支持断点续传（通过start_knowledge_id参数）
    - 支持批量处理（通过batch_size参数）
    - 支持强制重新处理（通过force_reprocess参数）
    """
    try:
        logger.info(f"启动批量嵌入处理: {request}")
        
        # 检查是否已有处理任务在运行
        if batch_embedding_service.is_running:
            return BatchEmbeddingResponse(
                success=False,
                message="已有批量处理任务在运行中，请等待完成或先停止当前任务",
                processed_count=batch_embedding_service.processed_count,
                total_count=batch_embedding_service.total_count,
                current_knowledge_id=batch_embedding_service.current_knowledge_id
            )
        
        # 启动批量处理
        result = await batch_embedding_service.process_batch_embedding(request)
        return result
        
    except Exception as e:
        logger.error(f"启动批量嵌入处理失败: {e}")
        return BatchEmbeddingResponse(
            success=False,
            message=f"启动批量嵌入处理失败: {str(e)}",
            processed_count=0,
            total_count=0
        )


@router.get("/api/batch/embedding/status", response_model=BatchEmbeddingStatus)
def get_batch_embedding_status():
    """
    获取批量文档嵌入处理状态
    """
    try:
        return batch_embedding_service.get_status()
    except Exception as e:
        logger.error(f"获取批量嵌入状态失败: {e}")
        return BatchEmbeddingStatus(
            is_running=False,
            processed_count=0,
            total_count=0,
            errors=[{"error": f"获取状态失败: {str(e)}"}]
        )


@router.post("/api/batch/embedding/stop")
def stop_batch_embedding():
    """
    停止批量文档嵌入处理
    """
    try:
        batch_embedding_service.stop_processing()
        return {
            "success": True,
            "message": "批量处理已停止"
        }
    except Exception as e:
        logger.error(f"停止批量嵌入处理失败: {e}")
        return {
            "success": False,
            "message": f"停止批量嵌入处理失败: {str(e)}"
        }


@router.post("/api/batch/embedding/reset")
def reset_batch_embedding():
    """
    重置批量文档嵌入处理状态
    """
    try:
        batch_embedding_service.reset_status()
        return {
            "success": True,
            "message": "批量处理状态已重置"
        }
    except Exception as e:
        logger.error(f"重置批量嵌入状态失败: {e}")
        return {
            "success": False,
            "message": f"重置批量嵌入状态失败: {str(e)}"
        }
