# Elasticsearch 知识检索系统使用指南

## 🚀 快速启动

### 1. 启动Elasticsearch

```bash
# 方法1：使用批处理脚本
start_elasticsearch.bat

# 方法2：手动启动
cd D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0
.\bin\elasticsearch.bat
```

### 2. 验证启动状态

访问以下地址验证ES是否正常启动：
- **集群健康**: http://localhost:9200/_cluster/health
- **节点信息**: http://localhost:9200/_nodes
- **索引列表**: http://localhost:9200/_cat/indices?v

## 📚 知识库设置

### 1. 运行设置脚本

```bash
# 安装Python依赖
pip install elasticsearch requests

# 运行设置脚本
python es_setup.py
```

### 2. 脚本功能

`es_setup.py` 脚本会自动完成以下操作：
- ✅ 检查Elasticsearch连接状态
- ✅ 创建知识库索引 `knowledge_base`
- ✅ 添加示例数据
- ✅ 测试搜索功能

## 🔍 搜索功能

### 1. 索引结构

知识库索引包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | long | 文档ID |
| `title` | text | 标题（支持中文分词） |
| `content` | text | 内容（支持中文分词） |
| `category` | keyword | 分类 |
| `tags` | keyword | 标签 |
| `author` | keyword | 作者 |
| `create_time` | date | 创建时间 |
| `update_time` | date | 更新时间 |
| `knowledge_id` | long | 知识ID |
| `chunk_id` | keyword | 文档块ID |
| `chunk_content` | text | 文档块内容 |
| `chunk_index` | integer | 文档块索引 |
| `file_name` | keyword | 文件名 |
| `file_type` | keyword | 文件类型 |
| `file_size` | long | 文件大小 |

### 2. 搜索API

#### 基础搜索
```bash
curl -X POST "localhost:9200/knowledge_base/_search" -H "Content-Type: application/json" -d'
{
  "query": {
    "multi_match": {
      "query": "Spring Boot",
      "fields": ["title^2", "content", "chunk_content"],
      "type": "best_fields"
    }
  },
  "highlight": {
    "fields": {
      "title": {},
      "content": {},
      "chunk_content": {}
    }
  }
}'
```

#### 分页搜索
```bash
curl -X POST "localhost:9200/knowledge_base/_search" -H "Content-Type: application/json" -d'
{
  "from": 0,
  "size": 10,
  "query": {
    "multi_match": {
      "query": "搜索关键词",
      "fields": ["title^2", "content", "chunk_content"]
    }
  }
}'
```

#### 分类搜索
```bash
curl -X POST "localhost:9200/knowledge_base/_search" -H "Content-Type: application/json" -d'
{
  "query": {
    "bool": {
      "must": [
        {"multi_match": {"query": "关键词", "fields": ["title", "content"]}},
        {"term": {"category": "技术文档"}}
      ]
    }
  }
}'
```

## 📝 添加知识

### 1. 单个文档添加

```bash
curl -X POST "localhost:9200/knowledge_base/_doc" -H "Content-Type: application/json" -d'
{
  "id": 3,
  "title": "新知识标题",
  "content": "知识内容...",
  "category": "技术文档",
  "tags": ["标签1", "标签2"],
  "author": "作者名",
  "create_time": "2024-01-17T10:00:00",
  "update_time": "2024-01-17T10:00:00",
  "knowledge_id": 3,
  "chunk_id": "chunk_3_1",
  "chunk_content": "文档块内容...",
  "chunk_index": 1,
  "file_name": "document.pdf",
  "file_type": "pdf",
  "file_size": 1024
}'
```

### 2. 批量添加

```bash
curl -X POST "localhost:9200/knowledge_base/_bulk" -H "Content-Type: application/json" -d'
{"index": {"_index": "knowledge_base"}}
{"id": 4, "title": "文档1", "content": "内容1", "category": "技术文档"}
{"index": {"_index": "knowledge_base"}}
{"id": 5, "title": "文档2", "content": "内容2", "category": "技术文档"}
'
```

## 🗂️ 管理操作

### 1. 查看索引信息
```bash
# 查看所有索引
curl "localhost:9200/_cat/indices?v"

# 查看索引映射
curl "localhost:9200/knowledge_base/_mapping?pretty"
```

### 2. 删除文档
```bash
# 根据ID删除
curl -X DELETE "localhost:9200/knowledge_base/_doc/1"

# 根据查询条件删除
curl -X POST "localhost:9200/knowledge_base/_delete_by_query" -H "Content-Type: application/json" -d'
{
  "query": {
    "term": {"category": "技术文档"}
  }
}'
```

### 3. 更新文档
```bash
curl -X POST "localhost:9200/knowledge_base/_update/1" -H "Content-Type: application/json" -d'
{
  "doc": {
    "title": "更新后的标题",
    "update_time": "2024-01-17T11:00:00"
  }
}'
```

## 🔧 配置说明

### 1. 中文分词

索引使用IK分词器进行中文分词：
- `ik_max_word`: 最细粒度分词
- `ik_smart`: 智能分词

### 2. 权重设置

搜索时不同字段的权重：
- `title`: 权重 2.0（标题更重要）
- `content`: 权重 1.0
- `chunk_content`: 权重 1.0

### 3. 高亮设置

搜索结果会高亮显示匹配的关键词：
- 使用 `<em>` 标签包裹高亮内容
- 支持多个字段同时高亮

## 🐛 故障排除

### 1. 连接问题
```bash
# 检查ES是否启动
curl "localhost:9200"

# 检查集群健康
curl "localhost:9200/_cluster/health"
```

### 2. 索引问题
```bash
# 删除索引重新创建
curl -X DELETE "localhost:9200/knowledge_base"

# 重新运行设置脚本
python es_setup.py
```

### 3. 内存问题
如果ES启动失败，可能需要调整内存设置：
- 编辑 `config/jvm.options`
- 设置 `-Xms1g` 和 `-Xmx1g`

## 📊 监控和统计

### 1. 集群统计
```bash
# 集群统计
curl "localhost:9200/_cluster/stats?pretty"

# 节点统计
curl "localhost:9200/_nodes/stats?pretty"
```

### 2. 索引统计
```bash
# 索引统计
curl "localhost:9200/knowledge_base/_stats?pretty"

# 搜索统计
curl "localhost:9200/knowledge_base/_stats/search?pretty"
```

## 🎯 最佳实践

### 1. 文档设计
- 合理设置字段类型
- 使用适当的分词器
- 设置合适的权重

### 2. 搜索优化
- 使用多字段匹配
- 合理设置分页大小
- 利用高亮功能

### 3. 性能优化
- 定期清理无用数据
- 监控集群健康状态
- 合理设置分片和副本

## 🔗 相关链接

- **Elasticsearch官方文档**: https://www.elastic.co/guide/
- **IK分词器**: https://github.com/medcl/elasticsearch-analysis-ik
- **REST API参考**: https://www.elastic.co/guide/en/elasticsearch/reference/current/rest-apis.html 