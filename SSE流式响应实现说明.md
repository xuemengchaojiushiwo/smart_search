# SSE流式响应实现说明

## 概述

RAG对话的流式接口使用Server-Sent Events (SSE) 技术实现，返回 `text/event-stream` 格式的数据流，为浏览器提供实时响应体验。

## SSE格式规范

SSE数据格式遵循以下规范：
```
event: <事件类型>
data: <JSON数据>

```

### 事件类型

1. **start**: 对话开始事件
2. **message**: 消息内容片段
3. **references**: 知识引用信息
4. **end**: 对话结束事件
5. **error**: 错误事件

## 服务端实现

### 响应头设置
```java
response.setContentType("text/event-stream");
response.setCharacterEncoding("UTF-8");
response.setHeader("Cache-Control", "no-cache");
response.setHeader("Connection", "keep-alive");
response.setHeader("Access-Control-Allow-Origin", "*");
response.setHeader("Access-Control-Allow-Headers", "Cache-Control");
```

### 事件发送示例
```java
PrintWriter writer = response.getWriter();

// 发送开始事件
writer.write("event: start\n");
writer.write("data: {\"message\":\"开始RAG对话\",\"sessionId\":\"" + sessionId + "\"}\n\n");
writer.flush();

// 发送消息片段
writer.write("event: message\n");
writer.write("data: {\"content\":\"消息内容\",\"index\":0}\n\n");
writer.flush();

// 发送结束事件
writer.write("event: end\n");
writer.write("data: {\"message\":\"RAG对话完成\"}\n\n");
writer.flush();
```

## 客户端实现

### JavaScript EventSource
```javascript
const eventSource = new EventSource('/api/chat/stream');

// 监听连接事件
eventSource.onopen = function(event) {
    console.log('连接已建立');
};

// 监听自定义事件
eventSource.addEventListener('start', function(event) {
    console.log('对话开始:', event.data);
});

eventSource.addEventListener('message', function(event) {
    const data = JSON.parse(event.data);
    console.log('收到消息片段:', data.content);
});

eventSource.addEventListener('end', function(event) {
    console.log('对话结束:', event.data);
    eventSource.close();
});

eventSource.addEventListener('error', function(event) {
    console.error('发生错误:', event.data);
    eventSource.close();
});
```

## 数据格式示例

### 开始事件
```
event: start
data: {"message":"开始RAG对话","sessionId":"session-123"}

```

### 消息片段
```
event: message
data: {"content":"RAG技术是","index":0}

event: message
data: {"content":"一种结合检索和生成的","index":1}

event: message
data: {"content":"人工智能技术。","index":2}

```

### 知识引用
```
event: references
data: {"count":3}

```

### 结束事件
```
event: end
data: {"message":"RAG对话完成","sessionId":"session-123"}

```

### 错误事件
```
event: error
data: {"message":"RAG对话失败: 服务不可用"}

```

## 浏览器兼容性

SSE技术在现代浏览器中有很好的支持：
- Chrome 6+
- Firefox 6+
- Safari 5+
- Edge 12+

## 优势

1. **实时性**: 数据实时传输，无需轮询
2. **简单性**: 基于HTTP协议，易于实现
3. **自动重连**: 浏览器自动处理连接断开和重连
4. **事件驱动**: 支持多种事件类型，便于处理不同状态

## 测试工具

### Python测试脚本
创建了 `test_sse_stream.py` 脚本来测试SSE流式响应：
- 测试SSE数据格式
- 模拟浏览器EventSource行为
- 验证事件处理

### HTML演示页面
创建了 `sse_demo.html` 页面来演示浏览器端的使用：
- 实时显示对话内容
- 事件日志记录
- 连接状态监控

## 使用场景

1. **实时对话**: 用户可以看到AI回答的实时生成过程
2. **进度反馈**: 通过不同事件类型提供进度信息
3. **错误处理**: 及时反馈错误信息
4. **知识引用**: 显示引用的知识来源

## 注意事项

1. **连接管理**: 需要正确处理连接的建立和断开
2. **错误处理**: 要处理网络错误和服务异常
3. **数据解析**: 客户端需要正确解析JSON格式的数据
4. **跨域问题**: 需要设置适当的CORS头
5. **资源清理**: 页面卸载时要关闭连接

## 总结

SSE流式响应为RAG对话提供了良好的用户体验，实现了真正的实时交互。通过标准的事件格式和简单的客户端API，可以轻松实现流式对话功能。 