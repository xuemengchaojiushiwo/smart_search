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
    username VARCHAR(100) NULL COMMENT '用户名(ldap返回)',
    staffid VARCHAR(50) UNIQUE NOT NULL COMMENT '工号',
    email VARCHAR(100) UNIQUE NULL COMMENT '邮箱',
    role VARCHAR(20) NULL COMMENT '兼容旧字段',
    staff_role VARCHAR(50) NULL COMMENT '员工角色(ldap)',
    system_role VARCHAR(50) NULL COMMENT '系统角色',
    workspace VARCHAR(200) NULL COMMENT '可管理的workspace(逗号分隔)',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
    created_time DATETIME NOT NULL COMMENT '创建时间',
    updated_time DATETIME COMMENT '更新时间',
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除标识'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 类目概念已移除，改用父子知识结构（folder/doc）

-- 知识表
CREATE TABLE IF NOT EXISTS knowledge (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL COMMENT '知识名称',
    description TEXT COMMENT '文字描述',
    parent_id BIGINT NULL COMMENT '父知识ID，根节点为NULL',
    node_type ENUM('folder','doc') DEFAULT 'doc' COMMENT '节点类型：folder=容器节点, doc=文档节点',
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
    parent_id BIGINT NULL COMMENT '父知识ID',
    node_type ENUM('folder','doc') DEFAULT 'doc' COMMENT '节点类型',
    tags JSON COMMENT '标签列表',
    effective_start_time DATETIME COMMENT '生效开始时间',
    effective_end_time DATETIME COMMENT '生效结束时间',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    created_time DATETIME NOT NULL COMMENT '创建时间',
    status TINYINT DEFAULT 1 COMMENT '状态：1-生效，0-失效',
    updated_by VARCHAR(50) COMMENT '更新人',
    updated_time DATETIME COMMENT '更新时间',
    search_count INT DEFAULT 0 COMMENT '搜索次数',
    download_count INT DEFAULT 0 COMMENT '下载次数',
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
    file_hash VARCHAR(64) COMMENT '内容哈希，用于去重',
    version_id BIGINT COMMENT '版本ID',
    version_number INT COMMENT '版本号',
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
    feedback_type ENUM('out_of_date','unclear','not_relevant') NULL COMMENT '反馈类型',
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

-- AI回答反馈（针对具体会话与回答消息）
CREATE TABLE IF NOT EXISTS chat_feedbacks (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    message_id VARCHAR(64) NOT NULL COMMENT '回答消息ID',
    user_id BIGINT NOT NULL COMMENT '用户ID',
    attitude ENUM('like','dislike') NOT NULL COMMENT '态度：点赞/点踩',
    feedback_type ENUM('out_of_date','unclear','not_relevant') NULL COMMENT '反馈类型',
    content TEXT COMMENT '点踩原因（可空）',
    created_time DATETIME NOT NULL DEFAULT NOW(),
    deleted TINYINT DEFAULT 0 COMMENT '逻辑删除',
    KEY idx_chat_fb_sess (session_id),
    KEY idx_chat_fb_msg (message_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- RAG会话（持久化）
CREATE TABLE IF NOT EXISTS chat_sessions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL UNIQUE COMMENT '会话ID',
    session_name VARCHAR(200) NULL COMMENT '会话名称',
    created_by VARCHAR(50) NOT NULL COMMENT '创建人',
    status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT '状态',
    message_count INT DEFAULT 0 COMMENT '消息数量',
    created_time DATETIME NOT NULL DEFAULT NOW(),
    last_active_time DATETIME NULL,
    KEY idx_chat_sessions_user (created_by),
    KEY idx_chat_sessions_last_active (last_active_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- RAG会话消息（持久化）
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(64) NOT NULL COMMENT '会话ID',
    message_id VARCHAR(64) NOT NULL UNIQUE COMMENT '消息ID',
    role ENUM('user','assistant') NOT NULL COMMENT '角色',
    content MEDIUMTEXT,
    references_json JSON NULL COMMENT '引用数据(JSON)',
    timestamp_ms BIGINT NOT NULL COMMENT '时间戳(毫秒)',
    created_by VARCHAR(50) NULL COMMENT '创建人（便捷按用户查询）',
    KEY idx_chat_msgs_session (session_id),
    KEY idx_chat_msgs_time (timestamp_ms)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
-- 用户部门角色表（保留）
CREATE TABLE IF NOT EXISTS user_dept_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    dept VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

