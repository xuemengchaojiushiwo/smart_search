from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import logging
import os
import tempfile
from pathlib import Path

# PyMuPDF Pro 统一文档处理
from pymupdf_font_fix import setup_pymupdf_pro_environment, test_pymupdf_pro_initialization

# 初始化 PyMuPDF Pro 环境
if not setup_pymupdf_pro_environment():
    logger.warning("PyMuPDF Pro 环境设置失败，将使用传统方案")

# 测试 PyMuPDF Pro 初始化
if not test_pymupdf_pro_initialization():
    logger.warning("PyMuPDF Pro 初始化失败，将使用传统方案")

import pymupdf.pro

# 文档处理相关
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import ElasticsearchStore
from langchain.schema import Document

# PyMuPDF4LLM 用于结构化分块
from pymupdf4llm import LlamaMarkdownReader

# ES相关
from elasticsearch import Elasticsearch
import hashlib

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Knowledge Base Python Service (PyMuPDF Pro)", version="2.0.0")

# 导入配置
from config import ES_CONFIG, DOCUMENT_CONFIG, EMBEDDING_CONFIG, RAG_CONFIG

# 初始化ES客户端
es_client = Elasticsearch(
    [f"http://{ES_CONFIG['host']}:{ES_CONFIG['port']}"],
    basic_auth=(ES_CONFIG['username'], ES_CONFIG['password']) if ES_CONFIG['username'] else None,
    verify_certs=ES_CONFIG['verify_certs']
)

# 初始化embedding模型
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_CONFIG['model_name'],
    model_kwargs={'device': EMBEDDING_CONFIG['device']}
)

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
    return {"message": "Knowledge Base Python Service (PyMuPDF Pro)"}

@app.post("/api/ldap/validate", response_model=LdapValidateResponse)
def validate_ldap_user(request: LdapValidateRequest):
    """
    LDAP用户验证
    这里应该调用实际的LDAP服务
    """
    logger.info(f"LDAP验证请求: {request.username}")
    
    try:
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
    except Exception as e:
        logger.error(f"LDAP验证异常: {e}")
        return LdapValidateResponse(
            success=False,
            message=f"LDAP验证服务异常: {str(e)}"
        )

def process_document_unified(file_path: str, knowledge_id: int, knowledge_name: str, 
                           description: str, tags: str, effective_time: str):
    """
    使用 PyMuPDF Pro 统一处理文档
    """
    logger.info(f"开始统一处理文档: {file_path}")
    
    try:
        # 使用 PyMuPDF Pro 打开文档
        doc = pymupdf.open(file_path)
        logger.info(f"成功打开文档，页数: {len(doc)}")
        
        # 提取文本
        text_parts = []
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"=== 第 {page_num + 1} 页 ===\n{text}")
        
        full_text = "\n\n".join(text_parts)
        logger.info(f"文本提取完成，总字符数: {len(full_text)}")
        
        # 使用 PyMuPDF4LLM 进行结构化分块
        try:
            reader = LlamaMarkdownReader()
            markdown_text = reader.load_data(file_path)
            
            # 使用 MarkdownHeaderTextSplitter 进行结构化分块
            splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=[
                    ("#", "标题1"),
                    ("##", "标题2"),
                    ("###", "标题3"),
                ]
            )
            chunks = splitter.split_text(markdown_text)
            logger.info(f"PyMuPDF4LLM 结构化分块完成，生成 {len(chunks)} 个chunks")
            
        except Exception as e:
            logger.warning(f"PyMuPDF4LLM 分块失败，使用传统分块: {e}")
            # 回退到传统分块
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=DOCUMENT_CONFIG['chunk_size'],
                chunk_overlap=DOCUMENT_CONFIG['chunk_overlap'],
                length_function=len,
            )
            chunks = text_splitter.split_text(full_text)
            chunks = [Document(page_content=chunk) for chunk in chunks]
        
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
        
        # 存入ES
        vectorstore = ElasticsearchStore(
            embedding=embeddings,
            index_name=ES_CONFIG['index'],
            es_connection=es_client
        )
        
        # 添加文档到向量存储
        vectorstore.add_documents(chunks)
        
        logger.info(f"文档处理完成: {file_path}, 生成了 {len(chunks)} 个chunks")
        
        return {
            "success": True,
            "chunks_count": len(chunks),
            "total_text_length": len(full_text),
            "processing_method": "pymupdf_pro"
        }
        
    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")

@app.post("/api/document/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    knowledge_id: int = None,
    knowledge_name: str = None,
    description: str = None,
    tags: str = None,
    effective_time: str = None
):
    """
    使用 PyMuPDF Pro 统一处理上传的文档
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
            # 使用统一的文档处理函数
            result = process_document_unified(
                temp_file_path,
                knowledge_id,
                knowledge_name,
                description,
                tags,
                effective_time
            )
            
            return DocumentProcessResponse(
                success=True,
                message=f"文档处理成功: {file.filename}",
                chunks_count=result["chunks_count"],
                knowledge_id=knowledge_id
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
    基于RAG的智能问答
    """
    logger.info(f"RAG对话请求: {request.question}")
    
    try:
        # 从ES检索相关文档
        vectorstore = ElasticsearchStore(
            embedding=embeddings,
            index_name=ES_CONFIG['index'],
            es_connection=es_client
        )
        
        # 检索最相关的文档
        docs_with_scores = vectorstore.similarity_search_with_score(
            request.question, 
            k=RAG_CONFIG['top_k']
        )
        
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
                relevance=float(score)
            )
            references.append(reference)
            
            # 添加到上下文
            context_parts.append(f"文档: {doc.metadata.get('knowledge_name', '未知')}\n内容: {doc.page_content}")
        
        # 构建完整上下文
        context = "\n\n".join(context_parts)
        
        # 模拟LLM回答（实际应该调用真实的LLM）
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
        
        # 检查PyMuPDF Pro
        import pymupdf.pro
        pymupdf_status = "available"
        
        return {
            "status": "healthy",
            "elasticsearch": "connected",
            "pymupdf_pro": pymupdf_status,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 