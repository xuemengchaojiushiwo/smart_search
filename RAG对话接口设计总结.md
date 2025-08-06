# RAG对话接口设计总结

## 设计理念

专注于RAG（Retrieval-Augmented Generation）对话功能，提供基于知识库的智能问答服务。

## 接口设计

### 1. 会话管理接口

#### 创建RAG会话
```
POST /api/chat/sessions
```
- **功能**: 创建一个新的RAG对话会话
- **参数**: 
  - `sessionName`: 会话名称
  - `description`: 会话描述
  - `knowledgeIds`: 指定知识库ID列表

#### 获取RAG会话列表
```
GET /api/chat/sessions
```
- **功能**: 获取当前用户的所有RAG对话会话
- **返回**: 会话列表，包含会话信息

### 2. RAG对话接口

#### RAG对话
```
POST /api/chat/rag
```
- **功能**: 基于知识库的智能问答
- **参数**:
  - `question`: 问题内容
  - `sessionId`: 会话ID（可选）
  - `knowledgeIds`: 指定知识库ID列表
  - `stream`: 是否流式响应

#### RAG流式对话
```
POST /api/chat/stream
```
- **功能**: 支持流式响应的RAG对话接口
- **参数**: 同RAG对话
- **响应**: SSE流式数据

## 数据结构设计

### ChatRequest
```java
public class ChatRequest {
    private String question;           // 问题内容
    private String userId;             // 用户ID
    private String sessionId;          // 会话ID（可选）
    private List<Long> knowledgeIds;   // 知识库ID列表
    private Boolean stream = false;    // 是否流式响应
}
```

### CreateSessionRequest
```java
public class CreateSessionRequest {
    private String sessionName;        // 会话名称
    private String description;        // 会话描述
    private List<Long> knowledgeIds;   // 知识库ID列表
}
```

### ChatSessionVO
```java
public class ChatSessionVO {
    private String sessionId;          // 会话ID
    private String sessionName;        // 会话名称
    private String description;        // 会话描述
    private List<Long> knowledgeIds;   // 知识库ID列表
    private String createdBy;          // 创建者
    private LocalDateTime createdTime; // 创建时间
    private LocalDateTime lastActiveTime; // 最后活跃时间
    private Integer messageCount;      // 消息数量
    private String status;             // 状态
}
```

## 接口优势

### 1. 功能专注
- **RAG专用**: 专门为RAG对话设计，功能清晰明确
- **知识库集成**: 支持指定知识库进行智能问答
- **会话管理**: 支持RAG会话的创建和管理

### 2. 灵活配置
- **知识库指定**: 可以指定特定的知识库进行RAG对话
- **会话可选**: 支持有会话和无会话两种模式
- **流式响应**: 支持普通响应和流式响应

### 3. 用户体验
- **连续对话**: 支持会话上下文保持
- **实时响应**: 支持流式输出，提升用户体验
- **知识引用**: 提供知识来源引用，增强可信度

## 使用场景

### 1. 创建RAG会话
```json
{
  "sessionName": "技术支持会话",
  "description": "用于技术问题咨询",
  "knowledgeIds": [1, 2, 3]
}
```

### 2. RAG对话（有会话）
```json
{
  "question": "请介绍一下知识库的功能",
  "sessionId": "session-001",
  "knowledgeIds": [1, 2, 3]
}
```

### 3. RAG对话（无会话）
```json
{
  "question": "什么是RAG技术？",
  "knowledgeIds": [1, 2, 3]
}
```

### 4. RAG流式对话
```json
{
  "question": "请详细介绍一下系统的架构设计",
  "sessionId": "session-002",
  "knowledgeIds": [1, 2, 3],
  "stream": true
}
```

## 测试验证

创建了测试脚本 `test_rag_chat.py` 来验证RAG对话接口：

1. **会话管理测试**: 创建RAG会话、获取会话列表
2. **RAG对话测试**: 测试基于知识库的对话
3. **流式对话测试**: 测试RAG流式响应功能
4. **无会话测试**: 测试无会话的RAG对话

## 总结

简化的RAG对话接口设计具有以下特点：

1. **功能专注**: 专门为RAG对话设计，避免功能冗余
2. **接口简洁**: 减少不必要的参数和接口
3. **易于使用**: 支持多种使用场景
4. **扩展性好**: 为未来功能扩展预留空间

这样的设计更符合专注于RAG对话的需求，提供了简洁而强大的RAG对话功能。 