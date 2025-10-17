# 知识库系统 - Java 服务

## 概述

本项目为知识库系统的 Java 后端（Spring Boot + MyBatis-Plus），提供认证、知识入库、检索、会话、反馈、类目管理等 REST API，并通过 HTTP 与 Python 服务进行 RAG 能力对接。

- 框架：Spring Boot 2.7.x、MyBatis-Plus、Spring Security、SpringDoc OpenAPI
- 运行环境：JDK 8+（编译目标 9）、Maven 3.8+
- 依赖服务：MySQL 8.x、Elasticsearch 7.17.x、Python 服务（默认 `http://localhost:8000`）

## 目录结构

```
src/
  main/
    java/com/knowledge/...
      config/        # 配置（CORS、ES、MyBatis-Plus、Swagger、Security 等）
      controller/    # 控制器（REST API）
      dto/           # 数据传输对象
      entity/        # 实体模型
      enums/         # 枚举
      exception/     # 全局异常与业务异常
      mapper/        # Mapper 接口
      security/      # 安全配置与过滤器
      service/       # 业务服务
      util/          # 工具类
      vo/            # 视图对象/返回模型
      KnowledgeBaseApplication.java  # 应用入口
    resources/
      application.yml
      db/            # 初始化/迁移 SQL
```

## 环境准备

- 安装 JDK 8+（JAVA_HOME 配置正确）
- 安装 Maven 3.8+
- 启动并可访问的 MySQL 8.x 与 Elasticsearch 7.17.x
- Python 服务（参见 `python_service/README.md`，默认地址 `http://localhost:8000`）

## 配置说明（application.yml）

关键配置位于 `src/main/resources/application.yml`：

- 服务端口：`server.port`（默认 8080）
- 数据库：通过环境变量覆盖，示例（Windows PowerShell）：
  - `$env:DB_HOST="localhost"`
  - `$env:DB_PORT="3306"`
  - `$env:DB_NAME="knowledge_base"`
  - `$env:DB_USER="root"`
  - `$env:DB_PASSWORD="your_password"`
- Python 服务地址：`python.service.url`（默认 `http://localhost:8000`）

提示（Windows）：请逐条执行命令，不要用 `&&` 串联。

## 初始化数据库

1. 创建数据库（如未自动创建）：
   - `knowledge_base`
2. 执行初始化脚本（任选其一，路径 `src/main/resources/db/`）：
   - `init.sql`（基础表）
   - `init_with_version_management.sql`（含版本管理表）
   - 如需增量变更，参考 `migrate_*.sql`

## 构建与运行

- 编译与打包：
```
mvn clean package -DskipTests
```

- 开发模式运行（热加载已启用）：
```
mvn spring-boot:run
```

- 直接运行打包产物（示例）：
```
java -jar target/knowledge-base-1.0.0.jar
```

## 常用环境变量（可覆盖 application.yml）

- `DB_HOST`、`DB_PORT`、`DB_NAME`、`DB_USER`、`DB_PASSWORD`
- `DB_USE_SSL`（默认 true）

在 PowerShell 中设置（示例）：
```
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_NAME="knowledge_base"
$env:DB_USER="root"
$env:DB_PASSWORD="your_password"
```

## 与 Python 服务联动

- Python 服务默认地址：`http://localhost:8000`
- 修改位置：`application.yml` → `python.service.url`
- 启动顺序建议：先启动 Python 服务，再启动 Java 服务

## API 文档（Swagger）

启动后访问：

- Swagger UI：`http://localhost:8080/swagger-ui.html` 或 `/swagger-ui/index.html`

## 常见问题（FAQ）

- 端口被占用：修改 `server.port`，或停止占用进程
- 无法连接数据库：检查环境变量与数据库网络连通性
- ES 版本不兼容：确保使用 7.17.x，对应客户端版本已在 `pom.xml` 指定
- Python 服务未启动：RAG 相关接口会失败，请先启动 Python 服务

## 测试

- 运行单测：
```
mvn test
```

## 代码规范

- 模块高内聚，控制器仅编排，请将业务逻辑下沉到 `service`
- 新增/修改逻辑需配套测试用例，确保可通过

## 版本与构建信息

- 版本：`pom.xml` → `<version>1.0.0</version>`
- 构建插件：`spring-boot-maven-plugin`、`maven-compiler-plugin`
