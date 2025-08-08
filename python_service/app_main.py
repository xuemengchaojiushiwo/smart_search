#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能知识库系统 - 主应用
整合PyMuPDF Pro + PyMuPDF4LLM + LangChain + 极客智坊API
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import logging
import os
import tempfile
from pathlib import Path
import requests

# PyMuPDF Pro 统一文档处理
from pymupdf_font_fix import setup_pymupdf_pro_environment, test_pymupdf_pro_initialization

# 为 PyMuPDF Pro 准备一个ASCII安全的字体目录，避免中文路径问题
SAFE_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts_tmp")
os.makedirs(SAFE_FONT_DIR, exist_ok=True)

# 约束 PyMuPDF 字体相关环境，避免扫描含中文路径的系统字体目录
os.environ['PYMUPDF_FONT_DIR'] = SAFE_FONT_DIR
os.environ['PYMUPDF_SKIP_FONT_INSTALL'] = '1'   # 跳过字体安装
os.environ['PYMUPDF_USE_SYSTEM_FONTS'] = '0'    # 不使用系统字体目录

# 可选导入 PyMuPDF 与 Pro 扩展
try:
    import pymupdf  # 主库
    PYMUPDF_AVAILABLE = True
except Exception:
    PYMUPDF_AVAILABLE = False

try:
    import pymupdf.pro  # Pro 扩展（可选）
    # 使用配置中的试用密钥，并强制使用SAFE_FONT_DIR，禁用自动字体路径检测
    try:
        from config import PYMUPDF_PRO_CONFIG
        trial_key = PYMUPDF_PRO_CONFIG.get('trial_key', '') if isinstance(PYMUPDF_PRO_CONFIG, dict) else ''
    except Exception:
        trial_key = ''

    try:
        if trial_key:
            pymupdf.pro.unlock(trial_key, fontpath=SAFE_FONT_DIR, fontpath_auto=False)
        else:
            pymupdf.pro.unlock(fontpath=SAFE_FONT_DIR, fontpath_auto=False)
        PYMUPDF_PRO_AVAILABLE = True
        logging.info("PyMuPDF Pro 解锁完成（使用安全字体目录）")
    except Exception as e:
        PYMUPDF_PRO_AVAILABLE = False
        logging.warning(f"PyMuPDF Pro 解锁失败，将使用免费版本: {e}")
except Exception:
    PYMUPDF_PRO_AVAILABLE = False

# 文档处理相关
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.schema import Document
import requests
import json

# PyMuPDF4LLM 用于结构化分块
try:
    from pymupdf4llm import LlamaMarkdownReader
    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False
    logging.warning("PyMuPDF4LLM 不可用，将使用传统分块")

# 引入基于本地 pymupdf4llm 的定位与预览能力
try:
    # 生成带 <sub>pos: ...</sub> 的 Markdown
    from pymupdf4llm.helpers.pymupdf_rag import to_markdown as to_md_with_pos
except Exception:
    to_md_with_pos = None

try:
    # 解析带位置的 Markdown → aligned_positions
    from python_service.md_pos_to_aligned import parse_md_with_pos, save_aligned
except Exception:
    try:
        from .md_pos_to_aligned import parse_md_with_pos, save_aligned
    except Exception:
        parse_md_with_pos = save_aligned = None

try:
    # 生成预览 PNG
    from python_service.preview_alignment import draw_preview
except Exception:
    try:
        from .preview_alignment import draw_preview
    except Exception:
        draw_preview = None

# ES相关
from elasticsearch import Elasticsearch
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="智能知识库系统", version="2.0.0")

# 导入配置
from config import (
    ES_CONFIG, DOCUMENT_CONFIG, EMBEDDING_CONFIG, RAG_CONFIG,
    PYMUPDF_PRO_CONFIG, CHUNKING_CONFIG, GEEKAI_API_KEY, GEEKAI_CHAT_URL,
    GEEKAI_EMBEDDING_URL, DEFAULT_EMBEDDING_MODEL
)

# 辅助：构建页文本与词级索引（用于bbox定位）
def build_page_text_and_word_index(page: "pymupdf.Page") -> (str, list):
    """返回 (page_text, word_entries), 其中 word_entries 为 [ (start, end, (x0,y0,x1,y1)) ]."""
    try:
        words = page.get_text("words")  # (x0,y0,x1,y1,word,block_no,line_no,word_no)
        # 排序：块→行→词
        words_sorted = sorted(words, key=lambda w: (int(w[5]), int(w[6]), int(w[7])))
        parts = []
        entries = []
        last_block, last_line = None, None
        current_pos = 0
        for w in words_sorted:
            x0, y0, x1, y1, token, bno, lno, wno = w
            key = (bno, lno)
            if last_block is None:
                # 首词，直接写
                parts.append(token)
                start = current_pos
                end = start + len(token)
                entries.append((start, end, (float(x0), float(y0), float(x1), float(y1))))
                current_pos = end
            else:
                if key != (last_block, last_line):
                    # 换行
                    parts.append("\n")
                    current_pos += 1
                    parts.append(token)
                    start = current_pos
                    end = start + len(token)
                    entries.append((start, end, (float(x0), float(y0), float(x1), float(y1))))
                    current_pos = end
                else:
                    # 同行词，空格分隔
                    parts.append(" ")
                    current_pos += 1
                    parts.append(token)
                    start = current_pos
                    end = start + len(token)
                    entries.append((start, end, (float(x0), float(y0), float(x1), float(y1))))
                    current_pos = end
            last_block, last_line = key
        page_text = "".join(parts)
        return page_text, entries
    except Exception:
        txt = page.get_text() or ""
        return txt, []

def compute_bbox_union_for_range(entries: list, start: int, end: int) -> list:
    """根据词级索引列表，计算覆盖 [start,end) 的bbox并集，返回 [x0,y0,x1,y1]，无则返回空列表。"""
    x0 = y0 = float("inf")
    x1 = y1 = float("-inf")
    found = False
    for (s, e, (a, b, c, d)) in entries:
        if e <= start or s >= end:
            continue
        found = True
        x0 = min(x0, a)
        y0 = min(y0, b)
        x1 = max(x1, c)
        y1 = max(y1, d)
    return [x0, y0, x1, y1] if found else []

# 初始化ES客户端
es_client = Elasticsearch(
    [f"http://{ES_CONFIG['host']}:{ES_CONFIG['port']}"],
    basic_auth=(ES_CONFIG['username'], ES_CONFIG['password']) if ES_CONFIG['username'] else None,
    verify_certs=ES_CONFIG['verify_certs']
)

# 极客API embedding函数
def get_embedding(text: str) -> list:
    """使用极客API获取文本嵌入向量"""
    try:
        url = GEEKAI_EMBEDDING_URL
        headers = {
            "Authorization": f"Bearer {GEEKAI_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": DEFAULT_EMBEDDING_MODEL,
            "input": [text],
            "intent": "search_document"
        }
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json().get("data", [{}])[0].get("embedding")
        else:
            logger.error(f"极客API embedding失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"极客API embedding异常: {e}")
        return None

# 请求模型
class LdapValidateRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    question: str
    user_id: str

class DocumentProcessRequest(BaseModel):
    knowledge_id: int
    knowledge_name: str
    description: str
    tags: List[str]
    effective_time: str

# 响应模型
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
    bbox_union: Optional[List[float]] = None
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

@app.get("/")
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

@app.post("/api/ldap/validate", response_model=LdapValidateResponse)
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

def process_document_unified(file_path: str, knowledge_id: int, knowledge_name: str, 
                           description: str, tags: str, effective_time: str):
    """
    使用 PyMuPDF Pro + PyMuPDF4LLM 统一处理文档
    """
    logger.info(f"开始统一处理文档: {file_path}")
    
    try:
        # 使用 PyMuPDF Pro 打开文档
        doc = pymupdf.open(file_path)
        logger.info(f"成功打开文档，页数: {len(doc)}")
        
        # 提取文本（页粒度），同时构建词级索引，便于后续 chunk bbox 计算
        page_texts: List[str] = []
        page_word_entries: List[List[tuple]] = []
        for page_num, page in enumerate(doc):
            p_text, p_entries = build_page_text_and_word_index(page)
            page_texts.append(p_text or "")
            page_word_entries.append(p_entries or [])
        full_text = "\n\n".join(page_texts)
        logger.info(f"文本提取完成，总字符数: {len(full_text)}")
        
        # 使用 PyMuPDF4LLM 进行结构化分块
        chunks: List[Document] = []
        if PYMUPDF4LLM_AVAILABLE:
            try:
                reader = LlamaMarkdownReader()
                md_nodes = reader.load_data(file_path)
                # LlamaMarkdownReader 返回的是节点列表，需拼接为字符串
                if isinstance(md_nodes, list):
                    markdown_text = "\n\n".join(str(n) for n in md_nodes)
                else:
                    markdown_text = str(md_nodes)

                splitter = MarkdownHeaderTextSplitter(headers_to_split_on=CHUNKING_CONFIG['markdown_headers'])
                chunks = splitter.split_text(markdown_text)
                logger.info(f"PyMuPDF4LLM 结构化分块完成，生成 {len(chunks)} 个chunks")
                
                # 如果chunks太少，使用更细粒度的分割
                if len(chunks) < CHUNKING_CONFIG['pymupdf4llm_config']['min_chunks']:
                    logger.info("chunks数量较少，使用更细粒度的分割")
                    # 使用传统分块作为补充
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=DOCUMENT_CONFIG['chunk_size'],
                        chunk_overlap=DOCUMENT_CONFIG['chunk_overlap'],
                        length_function=len,
                        separators=DOCUMENT_CONFIG['splitter_config']['separators'],
                        keep_separator=DOCUMENT_CONFIG['splitter_config']['keep_separator'],
                        is_separator_regex=DOCUMENT_CONFIG['splitter_config']['is_separator_regex']
                    )
                    additional_chunks = text_splitter.split_text(markdown_text)
                    additional_chunks = [Document(page_content=chunk) for chunk in additional_chunks]
                    chunks.extend(additional_chunks)
                    logger.info(f"补充分割后，总chunks数: {len(chunks)}")
                
            except Exception as e:
                logger.warning(f"PyMuPDF4LLM 分块失败，使用传统分块: {e}")
                chunks = []
        
        # 如果 PyMuPDF4LLM 分块失败或不可用，使用传统分块（页粒度，记录粗定位）
        if not chunks:
            def split_with_positions(text: str, chunk_size: int, overlap: int):
                results = []
                start = 0
                length = len(text)
                if chunk_size <= 0:
                    return results
                if overlap < 0:
                    overlap = 0
                step = max(1, chunk_size - overlap)
                while start < length:
                    end = min(start + chunk_size, length)
                    results.append((text[start:end], start, end))
                    if end == length:
                        break
                    start += step
                return results

            chunks = []
            for idx, page_text in enumerate(page_texts):
                parts = split_with_positions(
                    page_text,
                    DOCUMENT_CONFIG['chunk_size'],
                    DOCUMENT_CONFIG['chunk_overlap']
                )
                for _, (ct, cs, ce) in enumerate(parts):
                    doc_obj = Document(page_content=ct)
                    # 暂存页内位置，稍后写入ES时带上
                    doc_obj.metadata.update({
                        "page_num": idx + 1,
                        "char_start": cs,
                        "char_end": ce
                    })
                    chunks.append(doc_obj)
        
        # 为每个chunk添加元数据
        for chunk in chunks:
            chunk.metadata.update({
                "knowledge_id": knowledge_id,
                "knowledge_name": knowledge_name,
                "description": description,
                "tags": tags.split(",") if tags else [],
                "effective_time": effective_time,
                "source_file": os.path.basename(file_path),
                "file_type": Path(file_path).suffix.lower(),
                "processing_method": "pymupdf_pro"
            })

        # 集成：基于 PyMuPDF4LLM 生成“页级定位”与预览（不影响分块与入库）
        try:
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            out_dir = os.path.join(os.path.dirname(file_path), f"out_pdfllm_{base_name}")
            os.makedirs(out_dir, exist_ok=True)
            if to_md_with_pos is not None and parse_md_with_pos is not None and save_aligned is not None:
                md_text = to_md_with_pos(file_path, emit_positions=True)
                md_pos_path = os.path.join(out_dir, "pdfllm_document_with_pos.md")
                with open(md_pos_path, "w", encoding="utf-8") as f:
                    f.write(md_text)
                aligned_path = os.path.join(out_dir, "aligned_positions.json")
                items = parse_md_with_pos(md_pos_path)
                save_aligned(items, aligned_path)
                # 预览（可选）
                if draw_preview is not None:
                    preview_dir = os.path.join(out_dir, "preview")
                    os.makedirs(preview_dir, exist_ok=True)
                    draw_preview(file_path, aligned_path, preview_dir)
                logger.info(f"PDFLLM 定位与预览已生成: {out_dir}")
            else:
                logger.warning("PDFLLM 定位/预览依赖不可用，跳过该步骤")
        except Exception as e:
            logger.warning(f"PDFLLM 定位与预览生成失败: {e}")
        
        # 使用极客API生成embedding并存入ES
        stored_chunks = 0
        for i, chunk in enumerate(chunks):
            try:
                # 生成embedding
                embedding = get_embedding(chunk.page_content)
                if embedding is None:
                    logger.warning(f"chunk {i} embedding生成失败，跳过")
                    continue
                
                # 准备ES文档
                doc_id = hashlib.md5(f"{knowledge_id}_{i}_{chunk.page_content[:100]}".encode()).hexdigest()
                # 计算页内bbox（仅当有词级索引时）
                page_num = int(chunk.metadata.get("page_num") or -1)
                bbox_union = []
                if page_num > 0 and page_num - 1 < len(page_word_entries):
                    entries = page_word_entries[page_num - 1]
                    bbox_union = compute_bbox_union_for_range(entries, int(chunk.metadata.get("char_start") or 0), int(chunk.metadata.get("char_end") or 0))

                es_doc = {
                    "content": chunk.page_content,
                    "embedding": embedding,
                    "knowledge_id": knowledge_id,
                    "knowledge_name": knowledge_name,
                    "description": description,
                    "tags": tags.split(",") if tags else [],
                    "effective_time": effective_time,
                    "source_file": os.path.basename(file_path),
                    "file_type": Path(file_path).suffix.lower(),
                    "processing_method": "pymupdf_pro",
                    "chunk_index": i,
                    "chunk_type": "content",
                    "weight": 1.0,
                    "page_num": page_num,
                    "char_start": int(chunk.metadata.get("char_start") or -1),
                    "char_end": int(chunk.metadata.get("char_end") or -1),
                    "bbox_union": bbox_union
                }
                
                # 存储到ES
                es_client.index(index=ES_CONFIG['index'], id=doc_id, document=es_doc)
                stored_chunks += 1
                logger.info(f"已存储chunk {i+1}/{len(chunks)}")
                
            except Exception as e:
                logger.error(f"存储chunk {i} 失败: {e}")
                continue

        # 写入知识元信息块（便于检索知识名称/描述/标签/附件名）
        try:
            meta_content_parts = [
                str(knowledge_name or ""),
                str(description or ""),
                f"标签: {' '.join(tags.split(',') if tags else [])}",
                f"附件: {os.path.basename(file_path)}"
            ]
            meta_text = "\n".join([p for p in meta_content_parts if p])
            if meta_text.strip():
                meta_emb = get_embedding(meta_text)
                if meta_emb:
                    meta_id = hashlib.md5(f"meta_{knowledge_id}_{os.path.basename(file_path)}".encode()).hexdigest()
                    meta_doc = {
                        "content": meta_text,
                        "embedding": meta_emb,
                        "knowledge_id": knowledge_id,
                        "knowledge_name": knowledge_name,
                        "description": description,
                        "tags": tags.split(",") if tags else [],
                        "effective_time": effective_time,
                        "source_file": os.path.basename(file_path),
                        "file_type": Path(file_path).suffix.lower(),
                        "processing_method": "pymupdf_pro",
                        "chunk_index": -1,
                        "chunk_type": "knowledge_meta",
                        "weight": 1.2,
                        "page_num": -1,
                        "char_start": -1,
                        "char_end": -1
                    }
                    es_client.index(index=ES_CONFIG['index'], id=meta_id, document=meta_doc)
        except Exception as e:
            logger.warning(f"写入知识元信息块失败: {e}")
        
        logger.info(f"文档处理完成: {file_path}, 生成了 {len(chunks)} 个chunks，成功存储 {stored_chunks} 个chunks")
        
        return {
            "success": True,
            "chunks_count": stored_chunks,
            "total_text_length": len(full_text),
            "processing_method": "pymupdf_pro"
        }
        
    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")

@app.post("/api/document/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    knowledge_id: int = Form(None),
    knowledge_name: str = Form(None),
    description: str = Form(None),
    tags: str = Form(None),
    effective_time: str = Form(None)
):
    """
    使用 PyMuPDF Pro + PyMuPDF4LLM 统一处理上传的文档
    支持 PDF、Word、Excel、PowerPoint、TXT 等格式
    """
    logger.info(f"开始处理文档: {file.filename}, 知识ID: {knowledge_id}")
    
    try:
        # 检查文件类型
        file_extension = Path(file.filename).suffix.lower()
        
        # PyMuPDF Pro 支持的文件类型
        supported_extensions = {
            ".pdf", ".docx", ".doc", ".xlsx", ".xls", 
            ".pptx", ".ppt", ".txt", ".hwp", ".hwpx"
        }
        
        if file_extension not in supported_extensions:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_extension}")
        
        # 保存上传的文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # 处理文档
            result = process_document_unified(
                temp_file_path, knowledge_id, knowledge_name, 
                description, tags, effective_time
            )
            
            return DocumentProcessResponse(
                success=True,
                message=f"文档处理成功: {file.filename}",
                chunks_count=result["chunks_count"],
                knowledge_id=int(knowledge_id) if knowledge_id is not None else 0
            )
            
        finally:
            # 清理临时文件
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")

@app.post("/api/rag/chat", response_model=ChatResponse)
def chat_with_rag(request: ChatRequest):
    """
    基于RAG的智能问答，使用极客智坊API
    """
    logger.info(f"RAG对话请求: {request.question}")
    
    try:
        # 使用极客API生成问题embedding
        question_embedding = get_embedding(request.question)
        if question_embedding is None:
            raise HTTPException(status_code=500, detail="问题embedding生成失败")
        
        # 混合检索：BM25(知识名/描述/标签/附件名/正文) + 向量余弦
        search_body = {
            "size": RAG_CONFIG['top_k'],
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "query": request.question,
                                        "fields": [
                                            "knowledge_name^3",
                                            "description^2",
                                            "tags^2",
                                            "source_file^2",
                                            "content"
                                        ],
                                        "type": "best_fields"
                                    }
                                },
                                { "match": { "content": { "query": request.question, "boost": 1 } } }
                            ]
                        }
                    },
                    "script": {
                        "source": "0.6 * cosineSimilarity(params.qvec, 'embedding') * (doc['weight'].size()!=0?doc['weight'].value:1.0) + 0.4 * _score",
                        "params": { "qvec": question_embedding }
                    }
                }
            }
        }
        
        response = es_client.search(index=ES_CONFIG['index'], body=search_body)
        
        # 处理搜索结果
        docs_with_scores = []
        for hit in response['hits']['hits']:
            src = hit.get('_source', {})
            doc_content = src.get('content', '')
            score = float(hit.get('_score', 0.0))
            # 兜底清洗，避免 None 传入 Pydantic 模型
            metadata = {
                "knowledge_id": int(src.get("knowledge_id") or 0),
                "knowledge_name": str(src.get("knowledge_name") or "未知"),
                "description": str(src.get("description") or ""),
                "tags": src.get("tags") or [],
                "effective_time": str(src.get("effective_time") or ""),
                "attachments": src.get("attachments") or [],
                "source_file": src.get("source_file"),
                "page_num": src.get("page_num"),
                "chunk_index": src.get("chunk_index"),
                "chunk_type": src.get("chunk_type"),
                "bbox_union": src.get("bbox_union"),
                "char_start": src.get("char_start"),
                "char_end": src.get("char_end"),
            }
            doc = Document(page_content=doc_content, metadata=metadata)
            docs_with_scores.append((doc, score))
        
        # 构建知识引用
        references = []
        context_parts = []
        
        for doc, score in docs_with_scores:
            # 构建知识引用
            reference = KnowledgeReference(
                knowledge_id=doc.metadata.get("knowledge_id", 0),
                knowledge_name=doc.metadata.get("knowledge_name", "未知"),
                description=doc.metadata.get("description", ""),
                tags=doc.metadata.get("tags", []),
                effective_time=doc.metadata.get("effective_time", ""),
                attachments=doc.metadata.get("attachments", []),
                relevance=float(score),
                source_file=doc.metadata.get("source_file"),
                page_num=doc.metadata.get("page_num"),
                chunk_index=doc.metadata.get("chunk_index"),
                chunk_type=doc.metadata.get("chunk_type")
            )
            references.append(reference)
            
            # 添加到上下文
            pos = ""
            if doc.metadata.get("page_num") not in (None, -1):
                pos = f" (第{doc.metadata.get('page_num')}页)"
            context_parts.append(
                f"文档: {doc.metadata.get('knowledge_name', '未知')} - {doc.metadata.get('source_file', '')}{pos}\n内容: {doc.page_content}"
            )
        
        # 构建完整上下文
        context = "\n\n".join(context_parts)
        
        # 构建提示词
        prompt = f"""基于以下检索到的相关文档信息，请回答用户的问题。

相关文档信息：
{context}

用户问题：{request.question}

请基于上述文档信息，为用户提供准确、详细的回答。如果文档信息不足以回答问题，请说明情况。"""

        # 调用极客智坊API
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GEEKAI_API_KEY}"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的知识库助手，基于提供的文档信息回答用户问题。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(
                GEEKAI_CHAT_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content']
                logger.info("极客智坊API调用成功")
            else:
                logger.warning(f"极客智坊API调用失败: {response.status_code}")
                # 回退到模拟回答
                answer = f"基于检索到的相关文档，我为您提供以下信息：\n\n{context}\n\n这是基于RAG系统生成的回答。"
                
        except Exception as e:
            logger.error(f"极客智坊API调用异常: {e}")
            # 回退到模拟回答
            answer = f"基于检索到的相关文档，我为您提供以下信息：\n\n{context}\n\n这是基于RAG系统生成的回答。"
        
        return ChatResponse(
            answer=answer,
            references=references,
            session_id=f"session_{hash(request.question) % 10000}"
        )
        
    except Exception as e:
        logger.error(f"RAG对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"RAG对话失败: {str(e)}")

@app.get("/api/health")
def health_check():
    """
    健康检查
    """
    try:
        # 检查ES连接
        es_info = es_client.info()
        
        # 检查PyMuPDF / Pro 可用性
        pymupdf_status = "available" if PYMUPDF_AVAILABLE else "unavailable"
        pymupdf_pro_status = "available" if PYMUPDF_PRO_AVAILABLE else "unavailable"
        
        # 检查极客智坊API
        try:
            headers = {"Authorization": f"Bearer {GEEKAI_API_KEY}"}
            response = requests.get("https://geekai.co/api/v1/models", headers=headers, timeout=5)
            geekai_status = "available" if response.status_code == 200 else "unavailable"
        except:
            geekai_status = "unavailable"
        
        return {
            "status": "healthy",
            "elasticsearch": "connected",
            "pymupdf": pymupdf_status,
            "pymupdf_pro": pymupdf_pro_status,
            "geekai_api": geekai_status,
            "pymupdf4llm": "available" if PYMUPDF4LLM_AVAILABLE else "unavailable",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
