# 知识库管理系统

## 项目简介

基于Spring Boot + MyBatis Plus + MySQL的知识库管理系统，支持用户认证、类目管理、知识管理、搜索等功能。

## 技术栈

- **后端框架**: Spring Boot 2.7.14
- **ORM框架**: MyBatis Plus 3.5.3
- **数据库**: MySQL 8.0+
- **安全框架**: Spring Security + JWT
- **构建工具**: Maven
- **Python服务**: FastAPI (LDAP验证 + RAG对话)

## 快速开始

### 1. 环境要求

- JDK 8+
- Maven 3.6+
- MySQL 8.0+

### 2. 数据库配置

1. 创建数据库：
```sql
CREATE DATABASE knowledge_base DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 执行初始化脚本：
```bash
mysql -u root -p knowledge_base < src/main/resources/db/init.sql
```

3. 修改数据库连接配置：
编辑 `src/main/resources/application.yml` 文件，修改数据库连接信息：
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/knowledge_base?useUnicode=true&characterEncoding=utf8&useSSL=false&serverTimezone=Asia/Shanghai
    username: your_username
    password: your_password
```

### 3. 启动项目

#### 启动Java服务
```bash
# 编译项目
mvn clean compile

# 启动项目
mvn spring-boot:run
```

#### 启动Python服务
```bash
# 进入Python服务目录
cd python_service

# 安装依赖
pip install -r requirements.txt

# 启动Python服务
python app.py
```

项目启动后：
- Java服务地址：http://localhost:8080
- Python服务地址：http://localhost:8000

## API接口

### 用户认证

#### 用户登录
```
POST /api/auth/login
Content-Type: application/json

Request:
{
  "username": "admin",
  "password": "password"
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "token": "eyJhbGciOiJIUzUxMiJ9...",
    "expiresIn": 604800,
    "user": {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "ADMIN"
    }
  }
}
```

### 类目管理

#### 创建类目
```
POST /api/categories
Content-Type: application/json

Request:
{
  "name": "新类目",
  "level": 1,
  "parentId": null,
  "sortOrder": 1,
  "description": "类目描述"
}
```

#### 获取类目树
```
GET /api/categories/tree

Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "技术文档",
      "level": 1,
      "children": [
        {
          "id": 3,
          "name": "Java开发",
          "level": 2,
          "children": [...]
        }
      ]
    }
  ]
}
```

#### 更新类目
```
PUT /api/categories/{id}
Content-Type: application/json

Request:
{
  "name": "更新后的类目名称",
  "sortOrder": 2,
  "description": "更新后的描述",
  "changeReason": "更新原因"
}
```

#### 删除类目
```
DELETE /api/categories/{id}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "message": "删除成功"
  }
}
```

### 知识管理

#### 创建知识
```
POST /api/knowledge
Content-Type: application/json

Request:
{
  "name": "知识标题",
  "description": "知识描述",
  "categoryId": 6,
  "tags": ["标签1", "标签2"],
  "effectiveStartTime": "2024-01-01T00:00:00",
  "effectiveEndTime": "2024-12-31T23:59:59",
  "attachments": [
    {
      "fileName": "文档.pdf",
      "filePath": "/uploads/doc.pdf",
      "fileSize": 1024000,
      "fileType": "pdf"
    }
  ]
}
```

#### 获取知识列表
```
GET /api/knowledge?page=1&size=10

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "records": [
      {
        "id": 1,
        "name": "Spring Boot 入门指南",
        "description": "Spring Boot 框架的入门教程",
        "categoryId": 6,
        "categoryName": "Spring Boot",
        "tags": ["Spring Boot", "Java", "框架"],
        "searchCount": 10,
        "downloadCount": 5,
        "createdTime": "2024-01-01T10:00:00"
      }
    ],
    "total": 4,
    "size": 10,
    "current": 1
  }
}
```

#### 根据类目获取知识
```
GET /api/knowledge/category/{categoryId}?page=1&size=10
```

#### 获取热门知识
```
GET /api/knowledge/popular?limit=10

Response:
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 3,
      "name": "Vue.js 开发指南",
      "searchCount": 15,
      "downloadCount": 7
    }
  ]
}
```

#### 获取最新知识
```
GET /api/knowledge/latest?limit=10
```

#### 更新知识
```
PUT /api/knowledge/{id}
Content-Type: application/json

Request:
{
  "name": "更新后的知识标题",
  "description": "更新后的描述",
  "changeReason": "更新原因"
}
```

#### 删除知识
```
DELETE /api/knowledge/{id}
```

#### 处理知识文档
```
POST /api/knowledge/{id}/document
Content-Type: multipart/form-data

Request:
- file: 上传的文档文件（PDF、Word、Excel、PowerPoint、TXT）
- 其他参数通过路径参数传递

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "success": true,
    "message": "文档处理成功",
    "chunks_count": 15,
    "knowledge_id": 1
  }
}
```

### 搜索功能

#### 搜索知识
```
POST /api/search
Content-Type: application/json

Request:
{
  "query": "Spring Boot",
  "page": 1,
  "size": 10,
  "categoryId": 6,
  "tags": ["Java", "框架"]
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 1,
    "esResults": [
      {
        "id": 1,
        "name": "Spring Boot 入门指南",
        "description": "Spring Boot 框架的入门教程",
        "categoryName": "Spring Boot",
        "searchCount": 11
      }
    ],
    "ragResults": []
  }
}
```

#### 获取搜索建议
```
GET /api/search/suggest?q=spring
```

#### 获取推荐问题
```
GET /api/search/recommendations?limit=3

Response:
{
  "code": 200,
  "message": "success",
  "data": [
    "Spring Boot 配置",
    "MyBatis Plus 使用",
    "Vue.js 组件开发"
  ]
}
```

### 智能问答

#### 智能问答（普通响应）
```
POST /api/chat/chat
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "question": "什么是Spring Boot？",
  "userId": "admin"
}

Response:
{
  "code": 200,
  "message": "success",
  "data": {
    "answer": "基于知识库的回答: 什么是Spring Boot？",
    "sessionId": "uuid-session-id",
    "timestamp": 1703123456789,
    "references": [
      {
        "knowledgeId": 1,
        "knowledgeName": "示例知识1",
        "description": "这是一个示例知识描述",
        "tags": ["示例", "知识"],
        "effectiveTime": "2024-01-01 至 2024-12-31",
        "attachments": ["document1.pdf", "image1.jpg"],
        "relevance": 0.95
      }
    ]
  }
}
```

#### 智能问答（流式响应）
```
POST /api/chat/stream?sessionId={sessionId}
Content-Type: application/json
Authorization: Bearer {token}

Request:
{
  "question": "什么是Spring Boot？",
  "userId": "admin"
}

Response: Server-Sent Events (SSE) 流式响应
```

## 测试账号

系统预置了以下测试账号：

- **管理员账号**: admin / password
- **普通用户**: user1 / password
- **普通用户**: user2 / password

## 项目结构

```
src/main/java/com/knowledge/
├── config/          # 配置类
├── controller/      # 控制器
├── dto/           # 数据传输对象
├── entity/        # 实体类
├── exception/     # 异常处理
├── mapper/        # MyBatis Mapper
├── service/       # 业务服务
├── util/          # 工具类
└── vo/            # 视图对象
```

## 数据库设计

### 核心表结构

1. **users** - 用户表
2. **categories** - 三级类目表
3. **category_change_logs** - 类目变更历史表
4. **knowledge** - 知识表
5. **knowledge_versions** - 知识版本表
6. **attachments** - 附件表
7. **search_history** - 搜索历史表

### 设计特点

- 采用单表设计，不使用外键约束
- 在应用层保证数据一致性
- 使用逻辑删除
- 支持知识版本管理
- 记录搜索历史和统计

## 开发说明

### 1. 数据库设计
- 采用单表设计，不使用外键约束
- 在应用层保证数据一致性
- 使用逻辑删除

### 2. 安全设计
- 使用JWT Token进行身份认证
- Token默认过期时间7天
- 无状态设计，支持水平扩展

### 3. 异常处理
- 统一异常处理机制
- 业务异常和系统异常分离
- 详细的错误日志记录

### 4. 搜索功能
- 支持ES搜索（当前使用数据库搜索代替）
- 支持RAG搜索（预留接口）
- 搜索历史记录和推荐
- 搜索统计和热门排行

## 后续开发计划

1. **文件管理**: 实现文件上传下载功能
2. **权限管理**: 细粒度的权限控制
3. **Elasticsearch集成**: 实现真正的全文搜索
4. **缓存优化**: 添加Redis缓存支持
5. **流式响应优化**: 完善SSE流式响应实现 