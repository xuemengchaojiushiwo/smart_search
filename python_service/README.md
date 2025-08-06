# Python服务部署说明

## 功能概述

Python服务提供以下功能：
1. **LDAP用户验证**: 企业级用户认证
2. **文档处理**: 处理PDF、WORD、EXCEL、PowerPoint、TXT文件，使用langchain+专业库解析并存入ES
3. **RAG对话**: 从ES检索最相近的top5文档进行智能问答

## 环境要求

- Python 3.8+
- Elasticsearch 8.x
- 至少4GB内存（用于运行embedding模型）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. Elasticsearch配置

编辑 `config.py` 文件中的ES配置：

```python
ES_CONFIG = {
    "host": "localhost",  # ES服务器地址
    "port": 9200,        # ES端口
    "index": "knowledge_base",  # 索引名称
    "username": "elastic",  # ES用户名
    "password": "password",   # ES密码
    "verify_certs": False     # 是否验证证书
}
```

### 2. 文档处理配置

```python
DOCUMENT_CONFIG = {
    "chunk_size": 1000,      # 文本分块大小
    "chunk_overlap": 200,    # 分块重叠大小
    "allowed_extensions": {".pdf", ".docx", ".xlsx", ".pptx", ".txt"}  # 支持的文件类型
}
```

### 3. Embedding模型配置

```python
EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "device": "cpu"  # 或 "cuda" 如果有GPU
}
```

### 4. RAG配置

```python
RAG_CONFIG = {
    "top_k": 5,           # 检索最相近的文档数量
    "context_limit": 500   # 上下文长度限制
}
```

## 启动服务

```bash
python app.py
```

服务将在 http://localhost:8000 启动

## API接口

### 1. 健康检查
```
GET /api/health
```

### 2. LDAP用户验证
```
POST /api/ldap/validate
{
  "username": "admin",
  "password": "password"
}
```

### 3. 文档处理
```
POST /api/document/process
Content-Type: multipart/form-data

参数:
- file: 上传的文档文件
- knowledge_id: 知识ID
- knowledge_name: 知识名称
- description: 知识描述
- tags: 标签（逗号分隔）
- effective_time: 生效时间

支持的文件类型:
- PDF (.pdf): 使用PyMuPDF解析
- Word (.docx): 使用python-docx解析
- Excel (.xlsx): 使用openpyxl解析
- PowerPoint (.pptx): 使用python-pptx解析
- 文本 (.txt): 直接读取
```

### 4. RAG对话
```
POST /api/rag/chat
{
  "question": "用户问题",
  "user_id": "用户ID"
}
```

## 支持的文件类型

### PDF文件 (.pdf)
- 使用 PyMuPDFLoader 解析
- 提取文本内容和页面信息
- 支持多页文档

### Word文档 (.docx)
- 使用 python-docx 解析
- 提取段落文本和表格内容
- 保持文档结构

### Excel表格 (.xlsx)
- 使用 openpyxl 解析
- 提取所有工作表数据
- 按行组织数据，用"|"分隔单元格

### PowerPoint演示文稿 (.pptx)
- 使用 python-pptx 解析
- 提取幻灯片文本内容
- 按幻灯片组织内容

### 文本文件 (.txt)
- 直接读取文本内容
- 支持UTF-8编码

## 性能优化

### 1. 内存优化
- 使用临时文件处理大文档
- 及时清理临时文件
- 分批处理大量数据

### 2. 处理速度优化
- 并行处理多个文档
- 缓存embedding模型
- 优化文本分块策略

## 故障排除

### 1. 常见问题

**文档解析失败**
- 检查文件格式是否正确
- 确认文件未损坏
- 查看日志获取详细错误信息

**ES连接失败**
- 检查ES服务是否启动
- 确认连接配置正确
- 检查网络连接

**内存不足**
- 增加系统内存
- 减少chunk_size配置
- 分批处理大文档

### 2. 日志查看

```bash
# 查看服务日志
tail -f app.log

# 查看错误日志
grep ERROR app.log
```

## 扩展功能

### 1. 新增文件类型支持
在 `app.py` 的 `process_document` 函数中添加新的文件类型处理逻辑

### 2. 自定义文本分割
修改 `DOCUMENT_CONFIG` 中的分块参数

### 3. 增强元数据提取
在文档处理过程中提取更多元数据信息

### 4. 文档预处理
添加文档清洗、格式转换等预处理步骤 