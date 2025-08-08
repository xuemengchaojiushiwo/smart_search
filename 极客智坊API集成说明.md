# 极客智坊API集成说明

## 概述

本项目已集成极客智坊API，用于大模型调用功能。根据[极客智坊官方文档](https://docs.geekai.co/cn/docs/chat/base)，实现了完整的API调用功能。

## 文件结构

```
python_service/
├── geekai_client.py      # 极客智坊API客户端
├── app_with_geekai.py    # 集成极客智坊的主服务
├── config.py             # 配置文件
└── requirements_geekai.txt # 依赖文件

test_geekai_api.py        # API测试脚本
start_geekai_service.bat  # 启动脚本
```

## 配置信息

```python
# 极客智坊 API 配置
GEEKAI_API_KEY = "sk-fN48cWer80XHieChQuQqGGZNdcSivSn3b9EgpH5eu6MP4eST"
GEEKAI_API_BASE = "https://geekai.co/api/v1"
GEEKAI_EMBEDDING_URL = f"{GEEKAI_API_BASE}/embeddings"
GEEKAI_CHAT_URL = f"{GEEKAI_API_BASE}/chat/completions"
```

## 功能特性

### 1. 基础聊天功能
- 支持简单对话
- 支持流式响应
- 可配置模型和参数

### 2. RAG对话功能
- 基于文档内容的问答
- 支持流式RAG对话
- 自动构建提示词

### 3. 向量化功能
- 文本向量化
- 支持批量处理
- 多种向量化模型

### 4. 文档处理
- 模拟文档处理功能
- 支持知识库集成

## API接口

### 1. 健康检查
```
GET /health
```

### 2. 简单聊天
```
POST /chat
{
    "message": "你好",
    "model": "gpt-4o-mini"
}
```

### 3. 流式聊天
```
POST /chat/stream
{
    "message": "请介绍一下Java",
    "model": "gpt-4o-mini"
}
```

### 4. RAG对话
```
POST /rag
{
    "question": "什么是Spring Boot？",
    "context": ["Spring Boot是一个快速开发框架..."],
    "model": "gpt-4o-mini"
}
```

### 5. 流式RAG对话
```
POST /rag/stream
{
    "question": "什么是Spring Boot？",
    "context": ["Spring Boot是一个快速开发框架..."],
    "model": "gpt-4o-mini"
}
```

### 6. 向量化
```
POST /embeddings
{
    "texts": ["文本1", "文本2"],
    "model": "text-embedding-ada-002"
}
```

## 使用方法

### 1. 启动服务
```bash
# Windows
start_geekai_service.bat

# 或手动启动
cd python_service
pip install -r requirements_geekai.txt
python app_with_geekai.py
```

### 2. 测试API
```bash
python test_geekai_api.py
```

### 3. 在Java项目中集成
修改`PythonService.java`中的URL配置：
```java
private static final String PYTHON_SERVICE_URL = "http://localhost:5000";
```

## 核心类说明

### GeekAIClient
极客智坊API客户端，提供以下方法：
- `chat_completion()`: 基础聊天
- `chat_completion_stream()`: 流式聊天
- `get_embeddings()`: 向量化
- `simple_chat()`: 简单聊天
- `rag_chat()`: RAG对话
- `rag_chat_stream()`: 流式RAG对话

### 配置参数
- `DEFAULT_CHAT_MODEL`: 默认聊天模型 (gpt-4o-mini)
- `DEFAULT_EMBEDDING_MODEL`: 默认向量化模型 (text-embedding-ada-002)
- `HOST`: 服务主机 (0.0.0.0)
- `PORT`: 服务端口 (5000)

## 错误处理

服务包含完整的错误处理机制：
- API调用失败重试
- 网络异常处理
- 响应解析错误处理
- 详细的日志记录

## 性能优化

- 连接池复用
- 超时设置
- 流式响应
- 异步处理支持

## 安全考虑

- API密钥安全存储
- 请求验证
- 错误信息脱敏
- 访问控制

## 扩展功能

可以根据需要扩展以下功能：
- 多模型支持
- 对话历史管理
- 文档预处理
- 缓存机制
- 监控和统计

## 注意事项

1. 确保API密钥有效且有足够配额
2. 网络连接稳定
3. 服务端口未被占用
4. Python环境正确配置
5. 依赖包完整安装

## 故障排除

### 常见问题
1. **API调用失败**: 检查API密钥和网络连接
2. **服务启动失败**: 检查端口占用和依赖安装
3. **流式响应异常**: 检查网络稳定性和超时设置
4. **向量化失败**: 检查模型名称和文本格式

### 调试方法
1. 查看服务日志
2. 使用测试脚本验证
3. 检查网络连接
4. 验证API配置

## 更新日志

- v1.0.0: 初始版本，支持基础聊天和RAG对话
- 集成极客智坊API
- 支持流式响应
- 添加向量化功能 