# API测试指南

## 🎉 认证已关闭

所有接口的token验证已经关闭，现在可以自由测试所有API接口。

## 📋 可用的主要接口

### 1. ES搜索接口
```bash
# 搜索知识
GET http://localhost:8080/api/es/search?query=关键词&page=1&size=10

# 获取搜索总数
GET http://localhost:8080/api/es/search/count?query=关键词
```

### 2. Swagger UI文档
```
http://localhost:8080/swagger-ui/index.html
```

### 3. 健康检查
```bash
GET http://localhost:8080/actuator/health
```

## 🧪 测试方法

### 方法1: 使用PowerShell
```powershell
# 测试ES搜索
Invoke-WebRequest -Uri "http://localhost:8080/api/es/search?query=Spring Boot&page=1&size=10" -Method GET

# 测试ES搜索总数
Invoke-WebRequest -Uri "http://localhost:8080/api/es/search/count?query=Spring Boot" -Method GET

# 测试Swagger UI
Invoke-WebRequest -Uri "http://localhost:8080/swagger-ui/index.html" -Method GET
```

### 方法2: 使用Python脚本
```bash
# 运行快速测试
python quick_api_test.py

# 运行完整测试
python test_all_apis.py
```

### 方法3: 使用浏览器
直接在浏览器中访问：
- Swagger UI: http://localhost:8080/swagger-ui/index.html
- 健康检查: http://localhost:8080/actuator/health

### 方法4: 使用curl（如果安装了）
```bash
# 测试ES搜索
curl "http://localhost:8080/api/es/search?query=Spring Boot&page=1&size=10"

# 测试ES搜索总数
curl "http://localhost:8080/api/es/search/count?query=Spring Boot"
```

## 📊 测试数据

ES中已有以下测试数据：

1. **Spring Boot 入门指南**
   - ID: 1
   - 标题: Spring Boot 入门指南
   - 内容: Spring Boot是一个基于Spring框架的快速开发框架，简化了Spring应用的配置和部署。
   - 标签: Spring Boot,Java,框架
   - 作者: 张三

2. **Elasticsearch 搜索教程**
   - ID: 2
   - 标题: Elasticsearch 搜索教程
   - 内容: Elasticsearch是一个分布式搜索引擎，提供强大的全文搜索和分析功能。
   - 标签: Elasticsearch,搜索,分布式
   - 作者: 李四

## 🔍 搜索示例

### 搜索Spring Boot
```bash
GET http://localhost:8080/api/es/search?query=Spring Boot&page=1&size=10
```

### 搜索Elasticsearch
```bash
GET http://localhost:8080/api/es/search?query=Elasticsearch&page=1&size=10
```

### 搜索Java
```bash
GET http://localhost:8080/api/es/search?query=Java&page=1&size=10
```

## 📝 注意事项

1. **认证已关闭**: 所有接口现在都可以直接访问，无需token
2. **ES搜索正常**: ES搜索API工作正常，支持多字段搜索
3. **Swagger UI可用**: 可以通过Swagger UI查看和测试所有API
4. **测试完成后**: 建议在测试完成后重新启用认证

## 🎯 下一步

1. **测试所有接口**: 使用上述方法测试所有需要的接口
2. **添加测试数据**: 可以通过ES API添加更多测试数据
3. **验证功能**: 确保所有功能都按预期工作
4. **重新启用认证**: 测试完成后记得重新启用认证

## ✅ 当前状态

- ✅ 认证已关闭
- ✅ ES搜索API正常
- ✅ Swagger UI可访问
- ✅ 可以自由测试所有接口
- ✅ 测试数据已准备就绪

现在你可以开始测试所有API接口了！ 