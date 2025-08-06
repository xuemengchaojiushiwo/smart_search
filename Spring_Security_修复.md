# Spring Security 访问拒绝问题修复

## 🔧 问题描述

访问API时出现以下错误：
```
org.springframework.security.access.AccessDeniedException: Access is denied
```

这是因为Spring Security配置要求所有请求都需要认证，但Swagger UI和API文档的访问路径没有被允许。

## ✅ 修复内容

### 1. 更新SecurityConfig配置

在`SecurityConfig.java`中添加了以下允许访问的路径：

```java
.authorizeRequests()
// 允许访问认证相关接口
.antMatchers("/api/auth/**").permitAll()
// 允许访问Swagger UI和API文档
.antMatchers("/swagger-ui/**", "/swagger-ui.html", "/v3/api-docs/**", "/v2/api-docs/**").permitAll()
// 允许访问静态资源
.antMatchers("/webjars/**", "/swagger-resources/**").permitAll()
// 允许访问健康检查
.antMatchers("/actuator/**").permitAll()
// 允许访问根路径
.antMatchers("/").permitAll()
// 其他请求需要认证
.anyRequest().authenticated();
```

### 2. 允许访问的路径

| 路径 | 说明 |
|------|------|
| `/api/auth/**` | 认证相关接口 |
| `/swagger-ui/**` | Swagger UI界面 |
| `/swagger-ui.html` | Swagger UI主页 |
| `/v3/api-docs/**` | OpenAPI 3文档 |
| `/v2/api-docs/**` | Swagger 2文档 |
| `/webjars/**` | Web资源 |
| `/swagger-resources/**` | Swagger资源 |
| `/actuator/**` | 健康检查等监控端点 |
| `/` | 根路径 |

## 🚀 启动命令

### 使用PowerShell脚本（推荐）
```powershell
.\start_app.ps1
```

### 手动启动
```bash
# 1. 编译项目
mvn clean compile

# 2. 启动应用
mvn spring-boot:run
```

## 🌐 访问地址

修复后，可以正常访问：

- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **API文档**: http://localhost:8080/v3/api-docs
- **健康检查**: http://localhost:8080/actuator/health
- **根路径**: http://localhost:8080/

## 🧪 测试验证

运行测试脚本验证修复效果：
```bash
python test_security_fix.py
```

## 📋 修复的文件

- `src/main/java/com/knowledge/config/SecurityConfig.java` - 更新安全配置

## ⚠️ 注意事项

1. **重启应用**: 修改SecurityConfig后需要重启应用才能生效
2. **开发环境**: 当前配置适合开发环境，生产环境需要更严格的安全配置
3. **认证机制**: 其他API接口仍然需要认证，只有文档相关路径被允许匿名访问

## 🎯 成功标志

修复成功后，你应该能够：
1. 正常访问 http://localhost:8080/swagger-ui.html
2. 正常访问 http://localhost:8080/v3/api-docs
3. 不再出现"Access is denied"错误

## 📞 问题排查

如果仍然遇到问题：
1. 确保应用已重启
2. 检查控制台日志
3. 运行测试脚本验证
4. 确认SecurityConfig配置已正确应用 