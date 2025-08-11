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

# 添加当前目录到Python路径，以便导入本地包
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

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
    from mypymupdf4llm import LlamaMarkdownReader
    PYMUPDF4LLM_AVAILABLE = True
    print("✅ 成功导入 mypymupdf4llm.LlamaMarkdownReader")
except ImportError as e:
    PYMUPDF4LLM_AVAILABLE = False
    print(f"❌ PyMuPDF4LLM 不可用: {e}，将使用传统分块")

# 引入基于本地 mypymupdf4llm 的定位与预览能力
try:
    # 生成带 <sub>pos: ...</sub> 的 Markdown
    from mypymupdf4llm.helpers.pymupdf_rag import to_markdown as to_md_with_pos
    print("✅ 成功导入 mypymupdf4llm.helpers.pymupdf_rag.to_markdown")
except Exception as e:
    print(f"❌ 导入 mypymupdf4llm.helpers.pymupdf_rag.to_markdown 失败: {e}")
    to_md_with_pos = None

try:
    # 解析带位置的 Markdown → aligned_positions
    from md_pos_to_aligned import parse_md_with_pos, save_aligned
except Exception:
    parse_md_with_pos = save_aligned = None

try:
    # 生成预览 PNG
    from preview_alignment import draw_preview
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
                           description: str, tags: str, effective_time: str, original_filename: str = None):
    """
    使用 PyMuPDF 统一处理文档，生成PDFLLM风格的输出
    """
    logger.info(f"开始统一处理文档: {file_path}")
    
    try:
        # 使用 PyMuPDF 打开文档
        doc = pymupdf.open(file_path)
        logger.info(f"成功打开文档，页数: {len(doc)}")

        # 对非PDF文档，先转换为标准PDF
        input_suffix = Path(file_path).suffix.lower()
        use_pdf_doc = doc
        try:
            if input_suffix != ".pdf":
                logger.info("检测到非PDF文档，开始转换为PDF…")
                pdf_bytes = doc.convert_to_pdf()
                use_pdf_doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
                logger.info(f"转换完成，PDF页数: {len(use_pdf_doc)}")
        except Exception as e:
            logger.warning(f"转换PDF失败，回退使用原文档提取：{e}")
        
        # 使用PyMuPDF生成干净的Markdown内容
        md_text = generate_pdfllm_style_markdown(use_pdf_doc, original_filename or Path(file_path).name)
        logger.info(f"生成了干净的Markdown内容，长度: {len(md_text)}")
        
        # 单独提取位置信息映射
        position_mapping = extract_position_mapping(use_pdf_doc)
        logger.info(f"提取出 {len(position_mapping)} 个位置信息项")
        
        if not position_mapping:
            logger.warning("没有位置信息项，为所有chunks设置默认元数据")
        
        # 使用LangChain进行分块 - 保持适中的分块大小
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,  # 适中的分块大小
            chunk_overlap=300,  # 适中的重叠
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""]
        )
        
        # 创建文档对象
        doc_obj = Document(page_content=md_text, metadata={"source": file_path})
        chunks = text_splitter.split_documents([doc_obj])
        logger.info(f"分块完成，共 {len(chunks)} 个chunks")
        
        # 为每个chunk分配位置信息和增强元数据
        for i, chunk in enumerate(chunks):
            # 基础元数据
            chunk.metadata.update({
                "knowledge_id": knowledge_id,
                "knowledge_name": knowledge_name,
                "description": description,
                "tags": tags,
                "effective_time": effective_time,
                "source_file": original_filename or Path(file_path).name,
                "chunk_index": i,
                "chunk_type": "content"
            })
            
            # 增强元数据 - 只保留通用信息
            chunk.metadata.update({
                "document_name": original_filename or Path(file_path).name,  # 文档名称
                "document_type": "文档",  # 文档类型（通用）
                "keywords": extract_keywords_from_content(chunk.page_content),  # 关键标识词
            })
            
            # 尝试为chunk分配位置信息
            if position_mapping and len(position_mapping) > 0:
                # 简化位置匹配逻辑 - 让大模型自己判断
                chunk_text = chunk.page_content
                best_match = find_best_position_match(chunk_text, position_mapping)
                
                if best_match:
                    # 计算字符范围
                    char_start = md_text.find(chunk_text)
                    char_end = char_start + len(chunk_text) if char_start != -1 else -1
                    
                    chunk.metadata.update({
                        "page_num": best_match.get("page", 1),
                        "bbox_union": best_match.get("bbox", []),
                        "char_start": char_start,
                        "char_end": char_end
                    })
                    logger.info(f"Chunk {i} 分配位置信息: 页{best_match.get('page', 1)}, bbox={best_match.get('bbox', [])}, chars=({char_start}, {char_end})")
                else:
                    logger.warning(f"Chunk {i} 未找到匹配的位置信息")
                    # 设置默认位置信息
                    chunk.metadata.update({
                        "page_num": 1,
                        "bbox_union": [],
                        "char_start": -1,
                        "char_end": -1
                    })
            else:
                # 没有位置信息，设置默认值
                chunk.metadata.update({
                    "page_num": 1,
                    "bbox_union": [],
                    "char_start": -1,
                    "char_end": -1
                })
        
        # 生成embeddings并存储到ES
        chunks_with_embeddings = []
        for chunk in chunks:
            try:
                embedding = get_embedding(chunk.page_content)
                chunk.metadata["embedding"] = embedding
                chunks_with_embeddings.append(chunk)
            except Exception as e:
                logger.error(f"生成embedding失败: {e}")
                continue
        
        # 存储到ES
        if chunks_with_embeddings:
            store_chunks_to_es(chunks_with_embeddings, knowledge_id)
            logger.info(f"成功存储 {len(chunks_with_embeddings)} 个chunks到ES")
        else:
            logger.error("没有可存储的chunks")
            raise Exception("文档处理失败：没有可存储的chunks")
        
        # 清理资源
        doc.close()
        if use_pdf_doc != doc:
            use_pdf_doc.close()
        
        return {
            "success": True,
            "chunks_count": len(chunks_with_embeddings),
            "message": f"文档处理成功: {original_filename or Path(file_path).name}"
        }
        
    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        raise

def generate_pdfllm_style_markdown(doc, filename: str) -> str:
    """
    使用PyMuPDF生成干净的Markdown内容，位置信息不嵌入到文本中
    """
    content_lines = []
    
    # 添加文档标题
    content_lines.append(f"# {filename}")
    content_lines.append("")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 页面标题
        content_lines.append(f"## 第 {page_num + 1} 页")
        content_lines.append("")
        
        # 获取页面文本块
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    block_text = ""
                    
                    for line_idx, line in enumerate(block["lines"]):
                        line_text = ""
                        
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                # 只添加文本内容，不添加位置标签
                                line_text += text + " "
                        
                        if line_text.strip():
                            block_text += line_text.strip() + "\n"
                    
                    if block_text.strip():
                        # 检查是否可能是标题（基于字体大小）
                        max_font_size = max(span["size"] for line in block["lines"] for span in line["spans"])
                        if max_font_size > 12:  # 假设大于12pt的是标题
                            content_lines.append(f"### {block_text.strip()}")
                        else:
                            content_lines.append(block_text.strip())
                        content_lines.append("")
    
    # 合并所有内容
    return "\n".join(content_lines)

def extract_position_mapping(doc) -> List[Dict]:
    """
    单独提取位置信息映射，不嵌入到文本内容中
    """
    position_mapping = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    for line_idx, line in enumerate(block["lines"]):
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                position_mapping.append({
                                    "text": text,
                                    "page": page_num + 1,
                                    "bbox": span["bbox"],
                                    "font_size": span["size"],
                                    "font": span["font"],
                                    "block_idx": block_idx,
                                    "line_idx": line_idx,
                                    "span_idx": span_idx
                                })
    
    return position_mapping

def parse_pdfllm_style_markdown(md_text: str) -> List[Dict]:
    """
    解析PDFLLM风格的Markdown，提取位置信息
    """
    items = []
    
    # 匹配 <sub>pos: page=X, bbox=(...)</sub> 格式
    import re
    pattern = r'<sub>pos: page=(\d+), bbox=\(([^)]+)\)</sub>'
    
    matches = re.findall(pattern, md_text)
    for match in matches:
        page_num = int(match[0])
        bbox_str = match[1]
        
        try:
            # 解析bbox字符串 "x0, y0, x1, y1"
            bbox_parts = bbox_str.split(',')
            if len(bbox_parts) == 4:
                bbox = [float(part.strip()) for part in bbox_parts]
                
                # 提取对应的文本内容
                # 这里简化处理，实际可以根据需要调整
                items.append({
                    "page": page_num,
                    "bbox": bbox,
                    "char_start": -1,  # 简化处理
                    "char_end": -1,    # 简化处理
                    "text": ""          # 简化处理
                })
        except Exception as e:
            logger.warning(f"解析bbox失败: {bbox_str}, 错误: {e}")
            continue
                
    return items

def find_best_position_match(chunk_text: str, position_mapping: List[Dict]) -> Optional[Dict]:
    """
    为chunk找到最匹配的位置信息
    """
    if not position_mapping:
        return None
    
    # 改进的匹配逻辑：优先匹配包含在chunk中的文本
    chunk_text_lower = chunk_text.lower()
    chunk_words = set(chunk_text_lower.split())
    
    best_match = None
    best_score = 0
    
    # 第一轮：寻找精确包含的文本
    for pos_info in position_mapping:
        text = pos_info.get("text", "").strip()
        if text and text.lower() in chunk_text_lower:
            # 计算匹配度：文本长度与chunk长度的比例
            score = len(text) / max(len(chunk_text), 1)
            if score > best_score:
                best_score = score
                best_match = pos_info
    
    # 第二轮：如果没有找到精确包含的，尝试单词匹配
    if not best_match:
        for pos_info in position_mapping:
            text = pos_info.get("text", "").strip()
            if text:
                text_words = set(text.lower().split())
                # 计算单词重叠度
                overlap = len(chunk_words.intersection(text_words))
                if overlap > 0:
                    score = overlap / max(len(chunk_words), 1)
                    if score > best_score:
                        best_score = score
                        best_match = pos_info
    
    # 第三轮：如果还是没有找到，返回第一个有效的位置信息
    if not best_match and position_mapping:
        for pos_info in position_mapping:
            if pos_info.get("bbox") and len(pos_info.get("bbox", [])) == 4:
                return pos_info
    
    return best_match

def store_chunks_to_es(chunks: List[Document], knowledge_id: int):
    """
    将chunks存储到Elasticsearch
    """
    stored_count = 0
    
    for i, chunk in enumerate(chunks):
        try:
            # 生成文档ID
            doc_id = hashlib.md5(f"{knowledge_id}_{i}_{chunk.page_content[:100]}".encode()).hexdigest()
            
            # 准备ES文档
            es_doc = {
                "content": chunk.page_content,
                "embedding": chunk.metadata.get("embedding", []),
                "knowledge_id": chunk.metadata.get("knowledge_id", knowledge_id),
                "knowledge_name": chunk.metadata.get("knowledge_name", ""),
                "description": chunk.metadata.get("description", ""),
                "tags": chunk.metadata.get("tags", ""),
                "effective_time": chunk.metadata.get("effective_time", ""),
                "source_file": chunk.metadata.get("source_file", ""),
                "chunk_index": chunk.metadata.get("chunk_index", i),
                "chunk_type": chunk.metadata.get("chunk_type", "content"),
                "page_num": chunk.metadata.get("page_num", 1),
                "char_start": chunk.metadata.get("char_start", -1),
                "char_end": chunk.metadata.get("char_end", -1),
                "bbox_union": chunk.metadata.get("bbox_union", []),
                "weight": 1.0
            }
            
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
                description, tags, effective_time, file.filename
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
    基于知识库的智能问答
    """
    logger.info(f"RAG聊天请求: {request.question}")
    
    try:
        # 1. 向量搜索找到相关chunks
        question_embedding = get_embedding(request.question)
        if not question_embedding:
            return ChatResponse(
                answer="抱歉，无法生成问题的向量表示，请重试。",
                references=[],
                session_id=request.user_id
            )
        
        # 简化搜索逻辑 - 直接返回语义相似度最高的chunks
        search_query = {
            "size": 5,  # 返回前5个最相关的chunks
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": question_embedding}
                    }
                }
            },
            "_source": ["content", "metadata", "knowledge_id", "knowledge_name", "source_file", 
                       "page_num", "chunk_index", "bbox_union", "char_start", "char_end"]
        }
        
        search_response = es_client.search(index=ES_CONFIG['index'], body=search_query)
        hits = search_response.get('hits', {}).get('hits', [])
        
        if not hits:
            return ChatResponse(
                answer="抱歉，在知识库中没有找到相关信息。",
                references=[],
                session_id=request.user_id
            )
        
        # 2. 构建增强的上下文信息
        context_chunks = []
        for hit in hits:
            source = hit['_source']
            score = hit['_score']
            
            # 构建每个chunk的完整上下文信息
            chunk_info = {
                "content": source.get('content', ''),
                "metadata": {
                    "document_name": source.get('source_file', 'N/A'),
                    "document_type": "文档",  # 通用文档类型
                    "page_num": source.get('page_num', 'N/A'),
                    "chunk_index": source.get('chunk_index', 'N/A'),
                    "bbox_union": source.get('bbox_union', []),
                    "char_start": source.get('char_start', 'N/A'),
                    "char_end": source.get('char_end', 'N/A'),
                    "knowledge_name": source.get('knowledge_name', 'N/A'),
                    "relevance_score": round(score, 3)
                }
            }
            context_chunks.append(chunk_info)
        
        # 3. 构建增强的RAG提示词
        enhanced_prompt = build_enhanced_rag_prompt(request.question, context_chunks)
        
        # 4. 调用大模型生成答案
        answer = generate_ai_answer(enhanced_prompt)
        
        # 5. 构建引用信息
        references = []
        for chunk in context_chunks:
            metadata = chunk['metadata']
            references.append(KnowledgeReference(
                knowledge_id=0,  # 这里需要从chunk中获取
                knowledge_name=metadata.get('knowledge_name', ''),
                description=f"文档: {metadata.get('document_name', '')}",
                tags=[metadata.get('document_type', '')],
                effective_time="",
                attachments=[metadata.get('document_name', '')],
                relevance=metadata.get('relevance_score', 0.0),
                source_file=metadata.get('document_name', ''),
                page_num=metadata.get('page_num', 0),
                chunk_index=metadata.get('chunk_index', 0),
                chunk_type="content",
                bbox_union=metadata.get('bbox_union', []),
                char_start=metadata.get('char_start', 0),
                char_end=metadata.get('char_end', 0)
            ))
        
        return ChatResponse(
            answer=answer,
            references=references,
            session_id=request.user_id
        )
        
    except Exception as e:
        logger.error(f"RAG聊天失败: {e}")
        return ChatResponse(
            answer=f"抱歉，处理您的问题时出现错误：{str(e)}",
            references=[],
            session_id=request.user_id
        )

def build_enhanced_rag_prompt(question: str, context_chunks: List[Dict]) -> str:
    """
    构建增强的RAG提示词，让大模型能看到完整的上下文信息
    """
    context_parts = []
    
    for i, chunk in enumerate(context_chunks):
        metadata = chunk['metadata']
        
        # 构建每个chunk的详细上下文信息
        chunk_context = f"""
=== 引用 {i+1} ===
📄 文档名称: {metadata.get('document_name', 'N/A')}
📋 文档类型: {metadata.get('document_type', 'N/A')}
📖 页码: {metadata.get('page_num', 'N/A')}
🔢 块序: {metadata.get('chunk_index', 'N/A')}
🎯 相关性: {metadata.get('relevance_score', 'N/A')}
📍 坐标: {metadata.get('bbox_union', [])}
📝 内容: {chunk.get('content', '')}
"""
        context_parts.append(chunk_context)
    
    # 构建完整提示
    prompt = f"""
你是一个专业的文档知识助手。请基于以下信息回答问题。

每个引用都包含了完整的文档信息，包括：
- 文档名称和类型
- 页码和块序
- 相关性评分和位置坐标
- 具体内容

请仔细分析这些信息，并根据问题找到最准确的答案。

问题: {question}

参考信息:
{''.join(context_parts)}

请根据问题，从上述信息中找到最准确的答案。要求：
1. 直接回答问题，不要说"请查看引用信息"
2. 如果问题涉及特定文档，请确保答案来自正确的文档
3. 如果问题没有指定具体文档，请基于所有相关信息给出综合回答
4. 答案要具体、准确，包含关键数据
5. 用中文回答，并说明信息来源（如"根据文档第X页"）

请开始回答：
"""
    
    return prompt

def generate_ai_answer(prompt: str) -> str:
    """
    调用大模型生成答案
    """
    try:
        # 调用极客智坊API生成答案
        headers = {
            "Authorization": f"Bearer {GEEKAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-4o-mini",  # 使用合适的模型
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的文档知识助手，请基于提供的文档信息准确回答问题。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        response = requests.post(
            GEEKAI_CHAT_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                answer = result["choices"][0]["message"]["content"]
                return answer
            else:
                logger.error(f"API响应格式异常: {result}")
                return "抱歉，生成答案时出现格式错误，请重试。"
        else:
            logger.error(f"API调用失败: {response.status_code}, {response.text}")
            return f"抱歉，API调用失败（状态码：{response.status_code}），请重试。"
            
    except requests.exceptions.Timeout:
        logger.error("API调用超时")
        return "抱歉，生成答案超时，请重试。"
    except requests.exceptions.RequestException as e:
        logger.error(f"API请求异常: {e}")
        return f"抱歉，API请求异常：{str(e)}，请重试。"
    except Exception as e:
        logger.error(f"生成AI答案失败: {e}")
        return f"抱歉，生成答案时出现错误：{str(e)}，请重试。"

def extract_keywords_from_content(content: str) -> List[str]:
    """从内容提取关键标识词（通用版本）"""
    keywords = []
    content_lower = content.lower()
    
    # 通用关键词
    general_keywords = ["投资", "管理", "风险", "收益", "费用", "日期", "目标", "策略", "报告", "分析"]
    for keyword in general_keywords:
        if keyword in content_lower:
            keywords.append(keyword)
    
    # 文档结构关键词
    structure_keywords = ["标题", "章节", "表格", "图表", "附录", "摘要", "结论"]
    for keyword in structure_keywords:
        if keyword in content_lower:
            keywords.append(keyword)
    
    return keywords[:8]  # 限制关键词数量

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
            "mypymupdf4llm": "available" if PYMUPDF4LLM_AVAILABLE else "unavailable",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
