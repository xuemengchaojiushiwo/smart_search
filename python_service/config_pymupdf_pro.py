# Python服务配置文件 (PyMuPDF Pro 版本)

# Elasticsearch配置
ES_CONFIG = {
    "host": "localhost",
    "port": 9200,
    "index": "knowledge_base",
    "username": "elastic",
    "password": "password",
    "verify_certs": False
}

# 文档处理配置 (PyMuPDF Pro)
DOCUMENT_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "allowed_extensions": {
        ".pdf", ".docx", ".doc", ".xlsx", ".xls", 
        ".pptx", ".ppt", ".txt", ".hwp", ".hwpx"
    },
    "use_pymupdf_pro": True,
    "use_pymupdf4llm_chunking": True,
    "fallback_to_traditional": True
}

# Embedding模型配置
EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "device": "cpu"
}

# RAG配置
RAG_CONFIG = {
    "top_k": 5,  # 检索最相近的文档数量
    "context_limit": 500  # 上下文长度限制
}

# PyMuPDF Pro 配置
PYMUPDF_PRO_CONFIG = {
    "enabled": True,
    "trial_key": None,  # 需要设置试用密钥
    "supported_formats": {
        "word": [".doc", ".docx"],
        "excel": [".xls", ".xlsx"],
        "powerpoint": [".ppt", ".pptx"],
        "pdf": [".pdf"],
        "text": [".txt"],
        "hangul": [".hwp", ".hwpx"]
    },
    "processing_methods": {
        "primary": "pymupdf_pro",
        "fallback": "traditional",
        "chunking": "pymupdf4llm"
    }
}

# 分块策略配置
CHUNKING_CONFIG = {
    "use_pymupdf4llm_for_pdf": True,
    "fallback_to_current": True,
    "markdown_headers": [
        ("#", "标题1"),
        ("##", "标题2"), 
        ("###", "标题3"),
    ],
    "traditional_splitter": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "separators": ["\n\n", "\n", "。", "！", "？", ".", "!", "?"]
    }
} 