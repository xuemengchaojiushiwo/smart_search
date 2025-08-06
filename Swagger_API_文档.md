# Swagger API 文档

## 📖 概述

本项目已集成Swagger 3.0，提供了完整的API文档和调试功能。通过Swagger UI，前端开发人员可以：

- 查看所有API接口的详细信息
- 测试API接口功能
- 获取请求和响应的示例数据
- 了解API参数和返回值格式

## 🚀 访问方式

### Swagger UI 界面
启动应用后，访问以下地址查看API文档：
```
http://localhost:8080/swagger-ui/index.html
```

### API 文档 JSON
```
http://localhost:8080/v2/api-docs
```

## 📋 API 模块说明

### 1. 用户认证 (Auth)
- **路径**: `/api/auth`
- **功能**: 用户登录认证
- **主要接口**:
  - `POST /api/auth/login` - 用户登录

### 2. 知识管理 (Knowledge)
- **路径**: `/api/knowledge`
- **功能**: 知识库的增删改查
- **主要接口**:
  - `POST /api/knowledge` - 创建知识
  - `PUT /api/knowledge/{id}` - 更新知识
  - `DELETE /api/knowledge/{id}` - 删除知识
  - `GET /api/knowledge/{id}` - 获取知识详情
  - `GET /api/knowledge` - 获取知识列表
  - `GET /api/knowledge/category/{categoryId}` - 根据类目获取知识
  - `GET /api/knowledge/popular` - 获取热门知识
  - `GET /api/knowledge/latest` - 获取最新知识
  - `POST /api/knowledge/{id}/document` - 处理知识文档

### 3. 类目管理 (Category)
- **路径**: `/api/categories`
- **功能**: 知识类目的管理
- **主要接口**:
  - `POST /api/categories` - 创建类目
  - `PUT /api/categories/{id}` - 更新类目
  - `DELETE /api/categories/{id}` - 删除类目
  - `GET /api/categories/{id}` - 获取类目详情
  - `GET /api/categories/tree` - 获取类目树

### 4. 智能问答 (Chat)
- **路径**: `/api/chat`
- **功能**: RAG智能问答
- **主要接口**:
  - `POST /api/chat/chat` - 智能问答（普通响应）
  - `POST /api/chat/stream` - 智能问答（流式响应）

### 5. 搜索功能 (Search)
- **路径**: `/api/search`
- **功能**: 知识搜索
- **主要接口**:
  - `POST /api/search` - 搜索知识
  - `GET /api/search/suggest` - 获取搜索建议
  - `GET /api/search/recommendations` - 获取推荐问题

### 6. 测试接口 (Test)
- **路径**: `/api/test`
- **功能**: 提供示例数据和调试接口
- **主要接口**:
  - `GET /api/test/knowledge/sample` - 获取知识示例
  - `GET /api/test/knowledge/list/sample` - 获取知识列表示例
  - `GET /api/test/chat/request/sample` - 获取聊天请求示例
  - `GET /api/test/search/request/sample` - 获取搜索请求示例
  - `GET /api/test/knowledge/dto/sample` - 获取知识DTO示例
  - `POST /api/test/chat/simulate` - 模拟聊天响应
  - `POST /api/test/search/simulate` - 模拟搜索响应
  - `GET /api/test/status` - 获取API状态

## 🔧 使用说明

### 1. 查看API文档
1. 启动Spring Boot应用
2. 打开浏览器访问 `http://localhost:8080/swagger-ui/index.html`
3. 在Swagger UI界面中可以看到所有API接口

### 2. 测试API接口
1. 在Swagger UI中找到要测试的接口
2. 点击接口名称展开详情
3. 点击"Try it out"按钮
4. 填写请求参数（系统会提供默认值）
5. 点击"Execute"执行请求
6. 查看响应结果

### 3. 获取示例数据
- 使用测试接口获取各种示例数据
- 这些示例数据可以直接用于前端开发调试

## 📝 响应格式

所有API接口都使用统一的响应格式：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体的数据内容
  },
  "timestamp": 1640995200000
}
```

### 响应字段说明
- `code`: 响应状态码（200表示成功）
- `message`: 响应消息
- `data`: 响应数据
- `timestamp`: 时间戳

## 🔐 认证说明

### JWT Token认证
部分接口需要JWT Token认证：
1. 先调用登录接口获取token
2. 在请求头中添加：`Authorization: Bearer {token}`

### 示例
```bash
curl -X POST "http://localhost:8080/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

## 🛠️ 开发调试

### 1. 前端调试
- 使用测试接口获取示例数据
- 使用Swagger UI测试API功能
- 查看响应格式和数据结构

### 2. 参数说明
- 所有接口都提供了详细的参数说明
- 包含参数类型、是否必填、示例值等信息
- 支持默认值，方便测试

### 3. 错误处理
- 统一的错误响应格式
- 详细的错误信息说明
- 便于调试和问题定位

## 📚 相关文档

- [Spring Boot 官方文档](https://spring.io/projects/spring-boot)
- [Swagger 官方文档](https://swagger.io/docs/)
- [MyBatis Plus 文档](https://baomidou.com/)

## 🤝 技术支持

如有问题，请联系开发团队或查看项目日志获取详细信息。 