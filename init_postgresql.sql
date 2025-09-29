-- PostgreSQL 数据库初始化脚本
-- 创建数据库和用户（需要在 postgres 数据库中执行）

-- 创建数据库
CREATE DATABASE knowledge_base;

-- 创建用户（可选，也可以使用现有用户）
-- CREATE USER knowledge_user WITH PASSWORD 'your_password';
-- GRANT ALL PRIVILEGES ON DATABASE knowledge_base TO knowledge_user;

-- 切换到 knowledge_base 数据库
\c knowledge_base;

-- 创建扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255),
    email VARCHAR(100),
    staff_id VARCHAR(50),
    system_role VARCHAR(20) DEFAULT 'USER',
    staff_role VARCHAR(50),
    workspace TEXT,
    status INTEGER DEFAULT 1,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    display_name VARCHAR(100),
    department VARCHAR(100),
    position VARCHAR(100)
);

-- 工作空间表
CREATE TABLE workspaces (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE
);

-- 知识表
CREATE TABLE knowledge (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parent_id BIGINT,
    node_type VARCHAR(20) NOT NULL,
    tags TEXT,
    table_data JSONB,
    effective_start_time TIMESTAMP,
    effective_end_time TIMESTAMP,
    status INTEGER DEFAULT 1,
    created_by VARCHAR(50),
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    search_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    deleted BOOLEAN DEFAULT FALSE
);

-- 知识工作空间关联表
CREATE TABLE knowledge_workspace (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    workspace VARCHAR(50) NOT NULL,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- 附件表
CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    file_type VARCHAR(100),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_count INTEGER DEFAULT 0,
    file_hash VARCHAR(255),
    version_id BIGINT,
    version_number INTEGER,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- 知识版本表
CREATE TABLE knowledge_versions (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    version_number INTEGER NOT NULL,
    change_type VARCHAR(50),
    change_reason TEXT,
    content JSONB,
    created_by VARCHAR(50),
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- 知识反馈表
CREATE TABLE knowledge_feedbacks (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    feedback_type VARCHAR(50) NOT NULL,
    feedback_text TEXT,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- 知识收藏表
CREATE TABLE knowledge_favorites (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- 搜索历史表
CREATE TABLE search_history (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    query VARCHAR(500) NOT NULL,
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_count INTEGER,
    deleted BOOLEAN DEFAULT FALSE
);

-- 聊天会话表
CREATE TABLE chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(50) UNIQUE NOT NULL,
    session_name VARCHAR(255),
    created_by VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    message_count INTEGER DEFAULT 0,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 聊天消息表
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    message_id VARCHAR(50) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    references_json TEXT,
    timestamp_ms BIGINT,
    created_by VARCHAR(50) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

-- 聊天反馈表
CREATE TABLE chat_feedback (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    feedback_type VARCHAR(20) NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 知识点赞表
CREATE TABLE knowledge_likes (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX idx_knowledge_parent_id ON knowledge(parent_id);
CREATE INDEX idx_knowledge_node_type ON knowledge(node_type);
CREATE INDEX idx_knowledge_created_by ON knowledge(created_by);
CREATE INDEX idx_knowledge_workspace_knowledge_id ON knowledge_workspace(knowledge_id);
CREATE INDEX idx_knowledge_workspace_workspace ON knowledge_workspace(workspace);
CREATE INDEX idx_attachments_knowledge_id ON attachments(knowledge_id);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_knowledge_favorites_user_id ON knowledge_favorites(user_id);
CREATE INDEX idx_knowledge_favorites_knowledge_id ON knowledge_favorites(knowledge_id);

-- 插入默认数据
INSERT INTO workspaces (code, name, description) VALUES 
('WPB', 'WPB工作空间', 'WPB相关文档'),
('GPB', 'GPB工作空间', 'GPB相关文档'),
('ALL', '全部工作空间', '所有用户可访问');

-- 插入admin用户
INSERT INTO users (username, password, email, staff_id, system_role, staff_role, workspace, display_name) VALUES 
('666666', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDi', 'admin@company.com', '666666', 'Admin', 'Admin', 'WPB,GPB', '系统管理员');

-- 插入测试知识数据
INSERT INTO knowledge (name, description, parent_id, node_type, tags, created_by) VALUES 
('WPB', 'WPB工作空间根目录', 0, 'folder', '[]', '666666'),
('GPB', 'GPB工作空间根目录', 0, 'folder', '[]', '666666');

-- 关联知识到工作空间
INSERT INTO knowledge_workspace (knowledge_id, workspace) VALUES 
(1, 'WPB'),
(2, 'GPB');
