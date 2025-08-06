# 知识管理系统 API 接口文档

## 📋 文档说明

本文档描述了知识管理系统的所有API接口，供前端开发人员使用。

- **基础URL**: `http://localhost:8080`
- **API前缀**: `/api`
- **认证方式**: 当前已关闭认证，所有接口无需token
- **数据格式**: JSON
- **字符编码**: UTF-8

---

## 🔐 认证相关接口

### 1. 用户登录

**接口地址**: `POST /api/auth/login`

**接口描述**: 用户登录认证

**请求参数**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "ADMIN"
    }
  }
}
```

---

## 📚 知识管理接口

### 1. 创建知识（JSON格式）

**接口地址**: `POST /api/knowledge`

**接口描述**: 创建新的知识条目（JSON格式，不支持文件上传）

**请求参数**:
```json
{
  "name": "Spring Boot 实战指南",
  "description": "这是一个关于Spring Boot的实战指南，包含详细的开发教程和最佳实践。",
  "categoryId": 6,
  "tags": ["Spring Boot", "Java", "框架", "实战"],
  "effectiveStartTime": "2025-08-06T00:00:00",
  "effectiveEndTime": "2025-12-31T23:59:59",
  "attachments": [
    {
      "fileName": "spring-boot-guide.pdf",
      "filePath": "/uploads/spring-boot-guide.pdf",
      "fileSize": 1024000,
      "fileType": "application/pdf"
    }
  ],
  "changeReason": "新增Spring Boot实战指南"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "创建知识成功",
  "data": {
    "id": 1,
    "name": "Spring Boot 实战指南",
    "description": "这是一个关于Spring Boot的实战指南，包含详细的开发教程和最佳实践。",
    "categoryId": 6,
    "tags": "[\"Spring Boot\",\"Java\",\"框架\",\"实战\"]",
    "effectiveStartTime": "2025-08-06T00:00:00",
    "effectiveEndTime": "2025-12-31T23:59:59",
    "status": 1,
    "createdBy": "admin",
    "createdTime": "2025-08-06T10:30:00",
    "updatedBy": null,
    "updatedTime": "2025-08-06T10:30:00",
    "searchCount": 0,
    "downloadCount": 0
  }
}
```

### 2. 创建知识（支持文件上传）

**接口地址**: `POST /api/knowledge/create`

**接口描述**: 创建新的知识条目（表单格式，支持文件上传）

**Content-Type**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | String | ✅ | 知识名称 |
| description | String | ❌ | 知识描述 |
| categoryId | Long | ✅ | 类目ID |
| tags | String | ❌ | 标签（逗号分隔） |
| effectiveStartTime | String | ❌ | 生效开始时间（ISO格式） |
| effectiveEndTime | String | ❌ | 生效结束时间（ISO格式） |
| changeReason | String | ❌ | 变更原因 |
| files | MultipartFile[] | ❌ | 附件文件列表 |

**请求示例**:
```bash
curl -X POST "http://localhost:8080/api/knowledge/create" \
  -F "name=Spring Boot 实战指南" \
  -F "description=这是一个关于Spring Boot的实战指南" \
  -F "categoryId=6" \
  -F "tags=Spring Boot,Java,框架,实战" \
  -F "effectiveStartTime=2025-08-06T00:00:00" \
  -F "effectiveEndTime=2025-12-31T23:59:59" \
  -F "changeReason=新增Spring Boot实战指南" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "创建知识成功",
  "data": {
    "id": 2,
    "name": "Spring Boot 实战指南",
    "description": "这是一个关于Spring Boot的实战指南",
    "categoryId": 6,
    "tags": "[\"Spring Boot\",\"Java\",\"框架\",\"实战\"]",
    "effectiveStartTime": "2025-08-06T00:00:00",
    "effectiveEndTime": "2025-12-31T23:59:59",
    "status": 1,
    "createdBy": "admin",
    "createdTime": "2025-08-06T10:35:00",
    "updatedBy": null,
    "updatedTime": "2025-08-06T10:35:00",
    "searchCount": 0,
    "downloadCount": 0
  }
}
```

### 3. 获取知识列表

**接口地址**: `GET /api/knowledge`

**接口描述**: 分页获取知识列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | Integer | ❌ | 页码（默认1） |
| size | Integer | ❌ | 每页大小（默认10） |

**请求示例**:
```
GET /api/knowledge?page=1&size=10
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取知识列表成功",
  "data": {
    "records": [
      {
        "id": 1,
        "name": "Spring Boot 实战指南",
        "description": "这是一个关于Spring Boot的实战指南",
        "categoryId": 6,
        "categoryName": "Spring Boot",
        "tags": ["Spring Boot", "Java", "框架", "实战"],
        "effectiveStartTime": "2025-08-06T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "status": 1,
        "createdBy": "admin",
        "createdTime": "2025-08-06T10:30:00",
        "searchCount": 5,
        "downloadCount": 2
      }
    ],
    "total": 1,
    "size": 10,
    "current": 1,
    "pages": 1
  }
}
```

### 4. 获取知识详情

**接口地址**: `GET /api/knowledge/{id}`

**接口描述**: 根据ID获取知识详情

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | ✅ | 知识ID |

**请求示例**:
```
GET /api/knowledge/1
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取知识详情成功",
  "data": {
    "id": 1,
    "name": "Spring Boot 实战指南",
    "description": "这是一个关于Spring Boot的实战指南",
    "categoryId": 6,
    "tags": "[\"Spring Boot\",\"Java\",\"框架\",\"实战\"]",
    "effectiveStartTime": "2025-08-06T00:00:00",
    "effectiveEndTime": "2025-12-31T23:59:59",
    "status": 1,
    "createdBy": "admin",
    "createdTime": "2025-08-06T10:30:00",
    "updatedBy": null,
    "updatedTime": "2025-08-06T10:30:00",
    "searchCount": 5,
    "downloadCount": 2,
    "attachments": [
      {
        "id": 1,
        "fileName": "spring-boot-guide.pdf",
        "filePath": "uploads/abc123.pdf",
        "fileSize": 1024000,
        "fileType": "application/pdf",
        "fileHash": "a1b2c3d4e5f6...",
        "versionId": 1,
        "versionNumber": 1,
        "uploadTime": "2025-08-06T10:30:00",
        "downloadCount": 0
      },
      {
        "id": 2,
        "fileName": "spring-boot-config.docx",
        "filePath": "uploads/def456.docx",
        "fileSize": 2048000,
        "fileType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "fileHash": "b2c3d4e5f6g7...",
        "versionId": 1,
        "versionNumber": 1,
        "uploadTime": "2025-08-06T10:30:00",
        "downloadCount": 0
      }
    ]
  }
}
```

### 5. 更新知识

**接口地址**: `PUT /api/knowledge/{id}`

**接口描述**: 更新知识信息

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | ✅ | 知识ID |

**请求参数**:
```json
{
  "name": "Spring Boot 实战指南（更新版）",
  "description": "更新后的Spring Boot实战指南",
  "categoryId": 6,
  "tags": ["Spring Boot", "Java", "框架", "实战", "更新"],
  "effectiveStartTime": "2025-08-06T00:00:00",
  "effectiveEndTime": "2025-12-31T23:59:59",
  "changeReason": "更新知识内容"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "更新知识成功",
  "data": {
    "id": 1,
    "name": "Spring Boot 实战指南（更新版）",
    "description": "更新后的Spring Boot实战指南",
    "categoryId": 6,
    "tags": "[\"Spring Boot\",\"Java\",\"框架\",\"实战\",\"更新\"]",
    "effectiveStartTime": "2025-08-06T00:00:00",
    "effectiveEndTime": "2025-12-31T23:59:59",
    "status": 1,
    "createdBy": "admin",
    "createdTime": "2025-08-06T10:30:00",
    "updatedBy": "admin",
    "updatedTime": "2025-08-06T11:00:00",
    "searchCount": 5,
    "downloadCount": 2
  }
}
```

### 6. 删除知识

**接口地址**: `DELETE /api/knowledge/{id}`

**接口描述**: 删除指定知识

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | ✅ | 知识ID |

**请求示例**:
```
DELETE /api/knowledge/1
```

**响应示例**:
```json
{
  "code": 200,
  "message": "删除知识成功",
  "data": null
}
```

---

## 📄 文档处理接口

### 1. 处理单个文档

**接口地址**: `POST /api/knowledge/{id}/document`

**接口描述**: 上传并处理单个知识文档，存入ES

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | ✅ | 知识ID |

**Content-Type**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| file | MultipartFile | ✅ | 文档文件 |

**请求示例**:
```bash
curl -X POST "http://localhost:8080/api/knowledge/1/document" \
  -F "file=@document.pdf"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "文档处理成功",
  "data": {
    "fileName": "document.pdf",
    "fileSize": 1024000,
    "processedContent": "文档内容已处理并存入ES",
    "esIndex": "knowledge_base",
    "esId": "1_document.pdf"
  }
}
```

### 2. 处理多个文档

**接口地址**: `POST /api/knowledge/{id}/documents`

**接口描述**: 上传并处理多个知识文档，存入ES

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | ✅ | 知识ID |

**Content-Type**: `multipart/form-data`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| files | MultipartFile[] | ✅ | 文档文件列表 |

**请求示例**:
```bash
curl -X POST "http://localhost:8080/api/knowledge/1/documents" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx" \
  -F "files=@document3.txt"
```

**响应示例**:
```json
{
  "code": 200,
  "message": "文档处理成功",
  "data": {
    "processedFiles": 3,
    "knowledgeId": 1,
    "versionId": 2,
    "versionNumber": 2,
    "message": "成功处理 3 个文件",
    "results": {
      "document1.pdf": {
        "status": "success",
        "esIndex": "knowledge_base",
        "esId": "1_document1.pdf"
      },
      "document2.docx": {
        "status": "success",
        "esIndex": "knowledge_base",
        "esId": "1_document2.docx"
      },
      "document3.txt": {
        "status": "success",
        "esIndex": "knowledge_base",
        "esId": "1_document3.txt"
      }
    }
  }
}
```

---

## 🏷️ 类目管理接口

### 1. 获取类目列表

**接口地址**: `GET /api/category/list`

**接口描述**: 获取所有类目列表

**请求示例**:
```
GET /api/category/list
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取类目列表成功",
  "data": [
    {
      "id": 1,
      "name": "技术文档",
      "description": "技术相关文档",
      "parentId": null,
      "level": 1,
      "sortOrder": 1,
      "status": 1,
      "createdBy": "admin",
      "createdTime": "2025-08-06T10:00:00",
      "children": [
        {
          "id": 2,
          "name": "Java开发",
          "description": "Java开发相关",
          "parentId": 1,
          "level": 2,
          "sortOrder": 1,
          "status": 1,
          "createdBy": "admin",
          "createdTime": "2025-08-06T10:00:00",
          "children": [
            {
              "id": 6,
              "name": "Spring Boot",
              "description": "Spring Boot框架",
              "parentId": 2,
              "level": 3,
              "sortOrder": 1,
              "status": 1,
              "createdBy": "admin",
              "createdTime": "2025-08-06T10:00:00",
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

### 2. 创建类目

**接口地址**: `POST /api/category`

**接口描述**: 创建新的类目

**请求参数**:
```json
{
  "name": "新类目",
  "description": "新类目的描述",
  "parentId": 1,
  "level": 2,
  "sortOrder": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "创建类目成功",
  "data": {
    "id": 10,
    "name": "新类目",
    "description": "新类目的描述",
    "parentId": 1,
    "level": 2,
    "sortOrder": 1,
    "status": 1,
    "createdBy": "admin",
    "createdTime": "2025-08-06T12:00:00",
    "updatedBy": null,
    "updatedTime": "2025-08-06T12:00:00"
  }
}
```

### 3. 更新类目

**接口地址**: `PUT /api/category/{id}`

**接口描述**: 更新类目信息

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | ✅ | 类目ID |

**请求参数**:
```json
{
  "name": "更新后的类目名称",
  "description": "更新后的类目描述",
  "parentId": 1,
  "level": 2,
  "sortOrder": 1
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "更新类目成功",
  "data": {
    "id": 10,
    "name": "更新后的类目名称",
    "description": "更新后的类目描述",
    "parentId": 1,
    "level": 2,
    "sortOrder": 1,
    "status": 1,
    "createdBy": "admin",
    "createdTime": "2025-08-06T12:00:00",
    "updatedBy": "admin",
    "updatedTime": "2025-08-06T12:30:00"
  }
}
```

### 4. 删除类目

**接口地址**: `DELETE /api/category/{id}`

**接口描述**: 删除指定类目

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| id | Long | ✅ | 类目ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "删除类目成功",
  "data": null
}
```

---

## 🔍 搜索接口

### 1. 搜索知识

**接口地址**: `GET /api/search`

**接口描述**: 搜索知识内容

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | String | ✅ | 搜索关键词 |
| page | Integer | ❌ | 页码（默认1） |
| size | Integer | ❌ | 每页大小（默认10） |

**请求示例**:
```
GET /api/search?query=Spring Boot&page=1&size=10
```

**响应示例**:
```json
{
  "code": 200,
  "message": "搜索成功",
  "data": {
    "records": [
      {
        "id": 1,
        "name": "Spring Boot 实战指南",
        "description": "这是一个关于Spring Boot的实战指南",
        "categoryId": 6,
        "categoryName": "Spring Boot",
        "tags": ["Spring Boot", "Java", "框架", "实战"],
        "createdBy": "admin",
        "createdTime": "2025-08-06T10:30:00",
        "searchCount": 5,
        "downloadCount": 2,
        "score": 0.95,
        "highlights": [
          "这是一个关于<em>Spring Boot</em>的实战指南"
        ]
      }
    ],
    "total": 1,
    "size": 10,
    "current": 1,
    "pages": 1
  }
}
```

---

## 💬 聊天接口

### 1. 知识问答

**接口地址**: `POST /api/chat`

**接口描述**: 基于知识库进行智能问答

**请求参数**:
```json
{
  "message": "Spring Boot如何配置数据库连接？",
  "knowledgeIds": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "问答成功",
  "data": {
    "answer": "根据知识库中的Spring Boot实战指南，配置数据库连接的步骤如下：\n\n1. 在application.yml中添加数据库配置\n2. 添加相应的依赖\n3. 创建数据源配置类\n\n具体配置示例：\n```yaml\nspring:\n  datasource:\n    url: jdbc:mysql://localhost:3306/test\n    username: root\n    password: 123456\n    driver-class-name: com.mysql.cj.jdbc.Driver\n```",
    "knowledgeReferences": [
      {
        "id": 1,
        "name": "Spring Boot 实战指南",
        "relevance": 0.95,
        "excerpt": "Spring Boot数据库配置章节..."
      }
    ],
    "confidence": 0.92
  }
}
```

---

## 📊 统计接口

### 1. 获取热门知识

**接口地址**: `GET /api/knowledge/popular`

**接口描述**: 获取热门知识列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | Integer | ❌ | 返回数量（默认10） |

**请求示例**:
```
GET /api/knowledge/popular?limit=5
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取热门知识成功",
  "data": [
    {
      "id": 1,
      "name": "Spring Boot 实战指南",
      "description": "这是一个关于Spring Boot的实战指南",
      "categoryId": 6,
      "categoryName": "Spring Boot",
      "tags": ["Spring Boot", "Java", "框架", "实战"],
      "searchCount": 25,
      "downloadCount": 8,
      "createdTime": "2025-08-06T10:30:00"
    }
  ]
}
```

### 2. 获取最新知识

**接口地址**: `GET /api/knowledge/latest`

**接口描述**: 获取最新知识列表

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| limit | Integer | ❌ | 返回数量（默认10） |

**请求示例**:
```
GET /api/knowledge/latest?limit=5
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取最新知识成功",
  "data": [
    {
      "id": 2,
      "name": "Elasticsearch 搜索优化",
      "description": "关于Elasticsearch搜索性能优化的详细指南",
      "categoryId": 7,
      "categoryName": "Elasticsearch",
      "tags": ["Elasticsearch", "搜索", "优化", "性能"],
      "searchCount": 3,
      "downloadCount": 1,
      "createdTime": "2025-08-06T11:00:00"
    }
  ]
}
```

---

## 🔧 系统状态接口

### 1. 获取ES状态

**接口地址**: `GET /api/es/status`

**接口描述**: 获取Elasticsearch服务状态

**请求示例**:
```
GET /api/es/status
```

**响应示例**:
```json
{
  "code": 200,
  "message": "获取ES状态成功",
  "data": {
    "status": "GREEN",
    "clusterName": "elasticsearch",
    "nodeCount": 1,
    "indexCount": 1,
    "documentCount": 150,
    "health": {
      "cluster_name": "elasticsearch",
      "status": "green",
      "timed_out": false,
      "number_of_nodes": 1,
      "number_of_data_nodes": 1,
      "active_primary_shards": 1,
      "active_shards": 1,
      "relocating_shards": 0,
      "initializing_shards": 0,
      "unassigned_shards": 0,
      "delayed_unassigned_shards": 0,
      "number_of_pending_tasks": 0,
      "number_of_in_flight_fetch": 0,
      "task_max_waiting_in_queue_millis": 0,
      "active_shards_percent_as_number": 100.0
    }
  }
}
```

---

## 📝 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 错误响应示例

```json
{
  "code": 400,
  "message": "请求参数错误",
  "data": null,
  "errors": [
    {
      "field": "name",
      "message": "知识名称不能为空"
    }
  ]
}
```

---

## 🚀 使用说明

### 1. 接口调用流程

1. **创建知识**：
   - 使用 `POST /api/knowledge/create` 创建知识并上传附件
   - 或使用 `POST /api/knowledge` 创建知识（JSON格式）

2. **上传文档**：
   - 使用 `POST /api/knowledge/{id}/documents` 上传多个文档
   - 使用 `POST /api/knowledge/{id}/document` 上传单个文档

3. **搜索知识**：
   - 使用 `GET /api/search` 搜索知识内容
   - 使用 `GET /api/knowledge` 获取知识列表

4. **智能问答**：
   - 使用 `POST /api/chat` 进行知识问答

### 2. 文件上传说明

- 支持的文件格式：PDF、DOC、DOCX、TXT等
- 文件大小限制：建议不超过50MB
- 文件编码：UTF-8
- 文件命名：建议使用英文命名

### 3. 版本管理特性

- 每次修改知识都会自动创建新版本
- 相同内容的文件不会重复保存
- 支持版本历史追溯
- 记录变更原因和操作人

### 4. 搜索功能

- 支持全文搜索
- 支持标签搜索
- 支持类目筛选
- 搜索结果按相关性排序

---

## 📞 技术支持

如有问题，请联系开发团队或查看Swagger UI文档：
- **Swagger UI**: `http://localhost:8080/swagger-ui/index.html`
- **API文档**: 本文档
- **测试环境**: `http://localhost:8080` 