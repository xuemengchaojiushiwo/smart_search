-- 创建数据库
CREATE DATABASE IF NOT EXISTS knowledge_base DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE knowledge_base;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    status TINYINT DEFAULT 1,
    created_time DATETIME NOT NULL,
    updated_time DATETIME,
    deleted TINYINT DEFAULT 0
);

-- 类目表
CREATE TABLE IF NOT EXISTS categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    level INT NOT NULL,
    parent_id BIGINT,
    sort_order INT DEFAULT 0,
    status TINYINT DEFAULT 1,
    description TEXT,
    created_by VARCHAR(50) NOT NULL,
    created_time DATETIME NOT NULL,
    updated_by VARCHAR(50),
    updated_time DATETIME,
    deleted TINYINT DEFAULT 0
);

-- 知识表
CREATE TABLE IF NOT EXISTS knowledge (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category_id BIGINT NOT NULL,
    tags JSON,
    effective_start_time DATETIME,
    effective_end_time DATETIME,
    status TINYINT DEFAULT 1,
    created_by VARCHAR(50) NOT NULL,
    created_time DATETIME NOT NULL,
    updated_by VARCHAR(50),
    updated_time DATETIME,
    search_count INT DEFAULT 0,
    download_count INT DEFAULT 0,
    deleted TINYINT DEFAULT 0
);

-- 搜索历史表
CREATE TABLE IF NOT EXISTS search_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    query VARCHAR(500) NOT NULL,
    search_time DATETIME NOT NULL,
    result_count INT DEFAULT 0,
    deleted TINYINT DEFAULT 0
);

-- 插入测试数据
INSERT INTO users (username, email, role, created_time) VALUES 
('admin', 'admin@example.com', 'ADMIN', NOW()),
('user1', 'user1@example.com', 'USER', NOW());

INSERT INTO categories (name, level, parent_id, sort_order, created_by, created_time) VALUES 
('技术文档', 1, NULL, 1, 'admin', NOW()),
('产品手册', 1, NULL, 2, 'admin', NOW()),
('Java开发', 2, 1, 1, 'admin', NOW()),
('Python开发', 2, 1, 2, 'admin', NOW());

INSERT INTO knowledge (name, description, category_id, created_by, created_time) VALUES 
('Spring Boot入门指南', 'Spring Boot框架的基础知识和使用方法', 3, 'admin', NOW()),
('Python数据分析', '使用Python进行数据分析的教程', 4, 'admin', NOW());
