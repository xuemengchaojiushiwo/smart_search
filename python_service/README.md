# 智能知识库系统 - Python服务

## 概述

本服务是智能知识库系统的Python后端部分，主要提供以下功能：

1. 文档处理与分块
2. 文本嵌入生成
3. RAG（检索增强生成）聊天
4. 知识库搜索

## 新增功能：多语言嵌入模型支持

系统现已支持使用多种嵌入模型：

1. **OpenAI API (text-embedding-3-small)**：原始模型，通过极客智坊API调用
2. **本地模型 (multilingual-e5-large-instruct)**：新增支持，提供更好的中文理解能力
3. **自定义API**：预留接口，支持未来扩展

### 多语言模型优势

- 更好的中文语义理解
- 本地部署，不依赖外部API
- 更精确的mini-chunks识别
- 维度更小（1024维 vs 1536维），节省存储空间

## 安装依赖

```bash
pip install -r requirements.txt
```

如果只需要安装多语言嵌入模型相关依赖：

```bash
pip install sentence-transformers
```

## 配置说明

配置文件位于 `config.py`，主要配置项：

```python
# 嵌入维度
EMBEDDING_DIMS = 1024  # 从1536维改为1024维，适配multilingual-e5-large-instruct

# AI API 配置开关
AI_API_SWITCH = "local"  # 可选值: "geekai", "custom", "local"

# 默认模型配置
DEFAULT_EMBEDDING_MODEL = "multilingual-e5-large-instruct"

# 本地Embedding模型配置
LOCAL_EMBEDDING_MODEL = "intfloat/multilingual-e5-large-instruct"
LOCAL_EMBEDDING_BATCH_SIZE = 8  # 批处理大小
LOCAL_EMBEDDING_DEVICE = "cpu"  # 可选: "cpu", "cuda"
```

## 快速切换嵌入模型

使用 `switch_embedding.py` 脚本可以快速切换不同的嵌入模型：

```bash
# 切换到本地模型
python switch_embedding.py local

# 切换到极客智坊API
python switch_embedding.py geekai

# 切换到自定义API（需要自行配置）
python switch_embedding.py custom
```

## 测试嵌入功能

使用 `test_embedding.py` 脚本可以测试不同嵌入模型的效果：

```bash
python test_embedding.py
```

该脚本会测试多个中英文查询，并输出嵌入向量的维度、示例值和相似度信息。

## 注意事项

1. **首次加载本地模型**：首次加载 multilingual-e5-large-instruct 模型可能需要几分钟时间，请耐心等待。
2. **内存占用**：本地模型需要约2-3GB内存，请确保服务器有足够资源。
3. **模型下载**：首次使用本地模型时会自动下载模型文件（约1.1GB），请确保网络连接正常。

## 性能对比

| 模型 | 首次加载时间 | 平均嵌入时间/文本 | 内存占用 |
|------|-------------|-----------------|---------|
| text-embedding-3-small (API) | N/A | 不确定 (依赖网络) | 低 |
| multilingual-e5-large-instruct (本地) | ~7.5分钟 | 0.40秒 | ~2-3GB |

更多详细信息请参阅 `embedding_test_report.md`。

## 启动服务

推荐方式（以模块路径启动，避免相对导入问题）：

```bash
python -m uvicorn python_service.app_main:app --host 0.0.0.0 --port 8000
```

也可直接运行（适合本地快速调试）：

```bash
python python_service/app_main.py
```

服务默认在 `http://0.0.0.0:8000` 启动，端口可通过命令行 `--port` 指定或在配置中修改。

提示（Windows）：请单独执行每条命令，不要用 `&&` 串联。

## 模块结构与接口位置

本服务已完成模块化重构，核心模块如下：

- `app_main.py`：FastAPI 应用初始化与路由注册（对外应用入口）
- `routes.py`：对外 API 接口定义（所有路由都集中在此）
- `models.py`：Pydantic 请求/响应数据模型
- `document_processor.py`：文档解析与分块处理
- `es_client.py`：Elasticsearch 读写与嵌入向量存储
- `rag_engine.py`：RAG 检索与答案生成逻辑
- `utils.py`：通用工具方法

## API 列表（routes.py）

- GET `/`：根路径，返回系统信息
- GET `/api/health`：健康检查
- POST `/api/ldap/validate`：LDAP 验证
- POST `/ldap/verify`：LDAP 验证（模拟）
- POST `/api/document/process`：文档处理与分块
- POST `/api/rag/chat`：基于知识库的问答
- POST `/api/embedding`：获取文本嵌入
- POST `/api/diff/summary`：生成版本差异总结（HTML）

## 常见问题（FAQ）

- 启动时报相对导入错误：请优先使用模块方式启动
  - `python -m uvicorn python_service.app_main:app --host 0.0.0.0 --port 8000`
- 端口被占用：更换端口，例如 `--port 8001`
- 服务已在后台运行需停止：在 Windows 可使用任务管理器或 `taskkill /F /IM python.exe`

## 开发与测试

- 规范：各模块高内聚，仅通过最小接口交互，新增功能请补充相应测试
- 示例脚本：
  - `test_embedding.py`：嵌入功能测试
  - `test_rag_api.py`：RAG API 调试
  - `document_chunking_api.py`：文档分块 API 调试
- 嵌入模型切换：`python switch_embedding.py [local|geekai|custom]`
