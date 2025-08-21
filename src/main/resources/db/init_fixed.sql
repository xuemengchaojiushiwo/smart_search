-- 创建数据库
CREATE DATABASE IF NOT EXISTS knowledge_base DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE knowledge_base;

-- 设置连接字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT '邮箱',
    role VARCHAR(20) NOT NULL COMMENT '角色',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
    created_time DATETIME NOT NULL COMMENT '创建时间',
    updated_time DATETIME COMMENT '更新时间',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 三级类目表
CREATE TABLE IF NOT EXISTS categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '类目名称',
    level INT NOT NULL COMMENT '层级：1-一级类目，2-二级类目，3-三级类目',
    parent_id BIGINT COMMENT '父类目ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
    description TEXT COMMENT '类目描述',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    created_time DATETIME NOT NULL COMMENT '创建时间',
    updated_by VARCHAR(50) COMMENT '更新人',
    updated_time DATETIME COMMENT '更新时间',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 类目变更历史表
CREATE TABLE IF NOT EXISTS category_change_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    category_id BIGINT NOT NULL COMMENT '类目ID',
    change_type VARCHAR(20) NOT NULL COMMENT '变更类型：CREATE/UPDATE/DELETE',
    old_data JSON COMMENT '变更前数据',
    new_data JSON COMMENT '变更后数据',
    change_reason VARCHAR(500) COMMENT '变更原因',
    changed_by VARCHAR(50) NOT NULL COMMENT '变更人',
    changed_time DATETIME NOT NULL COMMENT '变更时间',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 知识表
CREATE TABLE IF NOT EXISTS knowledge (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL COMMENT '知识名称',
    description TEXT COMMENT '文字描述',
    category_id BIGINT NOT NULL COMMENT '三级类目ID',
    tags JSON COMMENT '标签列表',
    table_data JSON COMMENT '结构化表格数据(JSON): {columns:[{name,type}],rows:[...]}',
    effective_start_time DATETIME COMMENT '生效开始时间',
    effective_end_time DATETIME COMMENT '生效结束时间',
    status TINYINT DEFAULT 1 COMMENT '状态：1-生效，0-失效',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    created_time DATETIME NOT NULL COMMENT '创建时间',
    updated_by VARCHAR(50) COMMENT '更新人',
    updated_time DATETIME COMMENT '更新时间',
    search_count INT DEFAULT 0 COMMENT '搜索次数',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 知识版本表
CREATE TABLE IF NOT EXISTS knowledge_versions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    knowledge_id BIGINT NOT NULL COMMENT '知识ID',
    version_number INT NOT NULL COMMENT '版本号',
    name VARCHAR(200) NOT NULL COMMENT '知识名称',
    description TEXT COMMENT '文字描述',
    category_id BIGINT NOT NULL COMMENT '三级类目ID',
    tags JSON COMMENT '标签列表',
    effective_start_time DATETIME COMMENT '生效开始时间',
    effective_end_time DATETIME COMMENT '生效结束时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    created_time DATETIME NOT NULL COMMENT '创建时间',
    change_reason VARCHAR(500) COMMENT '变更原因',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 附件表
CREATE TABLE IF NOT EXISTS attachments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    knowledge_id BIGINT NOT NULL COMMENT '知识ID',
    file_name VARCHAR(200) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    file_size BIGINT NOT NULL COMMENT '文件大小(字节)',
    file_type VARCHAR(50) COMMENT '文件类型',
    upload_time DATETIME NOT NULL COMMENT '上传时间',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 点赞表
CREATE TABLE IF NOT EXISTS knowledge_likes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    knowledge_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_time DATETIME NOT NULL DEFAULT NOW(),
    deleted TINYINT DEFAULT 0,
    INDEX idx_kl_kid (knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 收藏表
CREATE TABLE IF NOT EXISTS knowledge_favorites (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    knowledge_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_time DATETIME NOT NULL DEFAULT NOW(),
    deleted TINYINT DEFAULT 0,
    INDEX idx_kf_kid (knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 反馈表
CREATE TABLE IF NOT EXISTS knowledge_feedbacks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    knowledge_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    type VARCHAR(50),
    content TEXT,
    created_time DATETIME NOT NULL DEFAULT NOW(),
    deleted TINYINT DEFAULT 0,
    INDEX idx_kfb_kid (knowledge_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 搜索历史表
CREATE TABLE IF NOT EXISTS search_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    query VARCHAR(500) NOT NULL COMMENT '搜索关键词',
    search_time DATETIME NOT NULL COMMENT '搜索时间',
    result_count INT COMMENT '结果数量',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入测试数据
INSERT INTO users (username, email, role, status, created_time) VALUES 
('admin', 'admin@example.com', 'ADMIN', 1, NOW()),
('user1', 'user1@example.com', 'USER', 1, NOW()),
('user2', 'user2@example.com', 'USER', 1, NOW());

-- 插入测试类目数据
INSERT INTO categories (name, level, parent_id, sort_order, status, description, created_by, created_time) VALUES 
('技术文档', 1, NULL, 1, 1, '技术相关文档', 'admin', NOW()),
('产品文档', 1, NULL, 2, 1, '产品相关文档', 'admin', NOW()),
('Java开发', 2, 1, 1, 1, 'Java开发相关', 'admin', NOW()),
('Python开发', 2, 1, 2, 1, 'Python开发相关', 'admin', NOW()),
('前端开发', 2, 1, 3, 1, '前端开发相关', 'admin', NOW()),
('Spring Boot', 3, 3, 1, 1, 'Spring Boot框架', 'admin', NOW()),
('MyBatis Plus', 3, 3, 2, 1, 'MyBatis Plus框架', 'admin', NOW()),
('Vue.js', 3, 5, 1, 1, 'Vue.js框架', 'admin', NOW()),
('React', 3, 5, 2, 1, 'React框架', 'admin', NOW());

-- 插入测试知识数据
INSERT INTO knowledge (name, description, category_id, tags, effective_start_time, effective_end_time, status, created_by, created_time, search_count, download_count) VALUES 
('Spring Boot 入门指南', 'Spring Boot 框架的入门教程，包含基础配置和使用方法', 6, '["Spring Boot", "Java", "框架"]', NOW(), NULL, 1, 'admin', NOW(), 10, 5),
('MyBatis Plus 使用手册', 'MyBatis Plus 的详细使用说明，包含CRUD操作和高级功能', 7, '["MyBatis Plus", "ORM", "数据库"]', NOW(), NULL, 1, 'admin', NOW(), 8, 3),
('Vue.js 开发指南', 'Vue.js 前端框架的开发指南，包含组件开发和状态管理', 8, '["Vue.js", "前端", "JavaScript"]', NOW(), NULL, 1, 'admin', NOW(), 15, 7),
('React 基础教程', 'React 框架的基础教程，包含JSX语法和组件开发', 9, '["React", "前端", "JavaScript"]', NOW(), NULL, 1, 'admin', NOW(), 12, 6);

-- 插入测试附件数据
INSERT INTO attachments (knowledge_id, file_name, file_path, file_size, file_type, upload_time, download_count) VALUES 
(1, 'spring-boot-guide.pdf', '/uploads/spring-boot-guide.pdf', 1024000, 'pdf', NOW(), 5),
(1, 'spring-boot-demo.zip', '/uploads/spring-boot-demo.zip', 2048000, 'zip', NOW(), 3),
(2, 'mybatis-plus-manual.pdf', '/uploads/mybatis-plus-manual.pdf', 1536000, 'pdf', NOW(), 3),
(3, 'vuejs-guide.pdf', '/uploads/vuejs-guide.pdf', 1280000, 'pdf', NOW(), 7),
(4, 'react-tutorial.pdf', '/uploads/react-tutorial.pdf', 1152000, 'pdf', NOW(), 6);

-- 插入测试搜索历史数据
INSERT INTO search_history (user_id, query, search_time, result_count) VALUES 
(1, 'Spring Boot', NOW() - INTERVAL 1 HOUR, 1),
(1, 'MyBatis Plus', NOW() - INTERVAL 2 HOUR, 1),
(2, 'Vue.js', NOW() - INTERVAL 30 MINUTE, 1),
(2, 'React', NOW() - INTERVAL 1 HOUR, 1),
(3, 'Java开发', NOW() - INTERVAL 45 MINUTE, 2); 