-- 创建数据库
CREATE DATABASE IF NOT EXISTS knowledge_base DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE knowledge_base;

-- 设置连接字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
SET character_set_connection=utf8mb4;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'USER',
    status TINYINT DEFAULT 1,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0
);

-- 类目表
CREATE TABLE IF NOT EXISTS categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id BIGINT,
    level INT DEFAULT 1,
    sort_order INT DEFAULT 0,
    status TINYINT DEFAULT 1,
    created_by VARCHAR(50),
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

-- 知识表
CREATE TABLE IF NOT EXISTS knowledge (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id BIGINT NOT NULL,
    tags JSON,
    effective_start_time DATETIME,
    effective_end_time DATETIME,
    status TINYINT DEFAULT 1,
    created_by VARCHAR(50),
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    search_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 知识版本表
CREATE TABLE IF NOT EXISTS knowledge_versions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    version_number INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id BIGINT NOT NULL,
    tags JSON,
    effective_start_time DATETIME,
    effective_end_time DATETIME,
    created_by VARCHAR(50),
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    change_reason VARCHAR(500),
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    UNIQUE KEY uk_knowledge_version (knowledge_id, version_number)
);

-- 附件表（添加hash和版本字段）
CREATE TABLE IF NOT EXISTS attachments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    file_hash VARCHAR(64),  -- SHA-256 hash值
    version_id BIGINT,      -- 关联的知识版本ID
    version_number INT,     -- 版本号
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    download_count INT DEFAULT 0,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id),
    FOREIGN KEY (version_id) REFERENCES knowledge_versions(id)
);

-- 附件版本表
CREATE TABLE IF NOT EXISTS attachment_versions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    attachment_id BIGINT NOT NULL,
    knowledge_id BIGINT NOT NULL,
    version_id BIGINT NOT NULL,
    version_number INT NOT NULL,
    file_name VARCHAR(200) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    file_hash VARCHAR(64),  -- SHA-256 hash值
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    change_reason VARCHAR(500),
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (attachment_id) REFERENCES attachments(id),
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id),
    FOREIGN KEY (version_id) REFERENCES knowledge_versions(id)
);

-- 搜索历史表
CREATE TABLE IF NOT EXISTS search_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT,
    query VARCHAR(500) NOT NULL,
    search_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    result_count INT,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 类目变更日志表
CREATE TABLE IF NOT EXISTS category_change_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    category_id BIGINT NOT NULL,
    change_type ENUM('CREATE', 'UPDATE', 'DELETE') NOT NULL,
    old_data JSON,
    new_data JSON,
    changed_by VARCHAR(50),
    change_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    change_reason VARCHAR(500),
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- 插入初始数据
INSERT INTO users (username, email, role) VALUES 
('admin', 'admin@example.com', 'ADMIN'),
('user1', 'user1@example.com', 'USER'),
('user2', 'user2@example.com', 'USER');

INSERT INTO categories (name, description, level, sort_order, created_by) VALUES 
('技术文档', '技术相关文档', 1, 1, 'admin'),
('Java开发', 'Java开发相关', 2, 1, 'admin'),
('Spring框架', 'Spring框架相关', 2, 2, 'admin'),
('数据库', '数据库相关', 2, 3, 'admin'),
('前端开发', '前端开发相关', 2, 4, 'admin'),
('Spring Boot', 'Spring Boot框架', 3, 1, 'admin'),
('Elasticsearch', 'Elasticsearch搜索引擎', 3, 2, 'admin'),
('MySQL', 'MySQL数据库', 3, 3, 'admin'),
('Vue.js', 'Vue.js前端框架', 3, 4, 'admin');

-- 创建索引
CREATE INDEX idx_knowledge_category ON knowledge(category_id);
CREATE INDEX idx_knowledge_status ON knowledge(status);
CREATE INDEX idx_knowledge_created_time ON knowledge(created_time);
CREATE INDEX idx_attachments_knowledge ON attachments(knowledge_id);
CREATE INDEX idx_attachments_version ON attachments(version_id);
CREATE INDEX idx_attachments_hash ON attachments(file_hash);
CREATE INDEX idx_knowledge_versions_knowledge ON knowledge_versions(knowledge_id);
CREATE INDEX idx_attachment_versions_version ON attachment_versions(version_id);
CREATE INDEX idx_search_history_user ON search_history(user_id);
CREATE INDEX idx_search_history_time ON search_history(search_time); 