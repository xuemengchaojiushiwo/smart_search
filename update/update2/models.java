#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class LdapValidateRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    question: str
    user_id: str
    source_file: Optional[str] = None  # 可选：指定特定文件名进行RAG检索
    workspace: Optional[str] = None  # 可选：指定工作空间进行RAG检索


class DocumentProcessRequest(BaseModel):
    knowledge_id: int
    knowledge_name: str
    description: str
    tags: List[str]
    effective_time: str


class LdapValidateResponse(BaseModel):
    success: bool
    message: str
    email: Optional[str] = None
    role: Optional[str] = None


class KnowledgeReference(BaseModel):
    knowledge_id: int
    knowledge_name: str
    description: str
    tags: List[str]
    effective_time: str
    attachments: List[str]
    relevance: float
    # 追溯定位增强
    source_file: Optional[str] = None
    page_num: Optional[int] = None
    chunk_index: Optional[int] = None
    chunk_type: Optional[str] = None
    # 新增：返回块坐标与字符范围，便于前端高亮
    bbox_union: Optional[List[List[float]]] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    references: List[KnowledgeReference]
    session_id: Optional[str] = None


class DocumentProcessResponse(BaseModel):
    success: bool
    message: str
    chunks_count: int
    knowledge_id: int
