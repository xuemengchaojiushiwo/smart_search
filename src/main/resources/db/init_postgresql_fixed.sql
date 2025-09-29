-- 创建数据库和用户（需要在 postgres 数据库中执行）

-- 创建数据库
CREATE DATABASE knowledge_base;

-- 切换到 knowledge_base 数据库
\c knowledge_base;

-- 创建扩展（如果需要）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 确保目标 schema 存在，并将 search_path 设为 knowledge_base 优先
CREATE SCHEMA IF NOT EXISTS knowledge_base;
SET search_path TO knowledge_base, public;

-- 直接按依赖顺序删除即可（幂等）
DROP TABLE IF EXISTS knowledge_favorites CASCADE;
DROP TABLE IF EXISTS knowledge_likes CASCADE;
DROP TABLE IF EXISTS knowledge_feedbacks CASCADE;
DROP TABLE IF EXISTS attachments CASCADE;
DROP TABLE IF EXISTS knowledge_versions CASCADE;
DROP TABLE IF EXISTS knowledge_workspace CASCADE;
DROP TABLE IF EXISTS search_history CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS chat_feedbacks CASCADE;
DROP TABLE IF EXISTS chat_sessions CASCADE;
DROP TABLE IF EXISTS workspaces CASCADE;
DROP TABLE IF EXISTS knowledge CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS user_dept_role CASCADE;

-- 用户表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(100) NULL, -- 用户名(ldap返回)
    staffid VARCHAR(50) UNIQUE NOT NULL, -- 工号
    email VARCHAR(100) UNIQUE NULL, -- 邮箱
    role VARCHAR(20) NULL, -- 兼容旧字段
    display_name VARCHAR(150) NULL, -- 显示名称
    profile_picture VARCHAR(255) NULL, -- 头像URL
    password VARCHAR(255) NULL, -- 密码(迁移保留)
    last_login TIMESTAMP NULL, -- 上次登录时间
    date_joined TIMESTAMP NULL, -- 注册时间(迁移保留)
    staff_role VARCHAR(50) NULL, -- 员工角色(ldap)
    system_role VARCHAR(50) NULL, -- 系统角色
    workspace VARCHAR(200) NULL, -- 可管理的workspace(逗号分隔)
    status INTEGER DEFAULT 1, -- 状态：1-启用，0-禁用
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_time TIMESTAMP NULL, -- 更新时间
    deleted SMALLINT DEFAULT 0 -- 逻辑删除标识(0/1)
);

-- 知识表
CREATE TABLE knowledge (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL, -- 知识名称
    description TEXT, -- 文字描述
    parent_id BIGINT NULL, -- 父知识ID，根节点为NULL
    node_type VARCHAR(10) DEFAULT 'doc' CHECK (node_type IN ('folder','doc')), -- 节点类型：folder=容器节点, doc=文档节点
    tags JSONB, -- 标签列表
    table_data JSONB, -- 结构化表格数据(JSON): {columns:[{name,type}],rows:[...]}
    effective_start_time TIMESTAMP NULL, -- 生效开始时间
    effective_end_time TIMESTAMP NULL, -- 生效结束时间
    status INTEGER DEFAULT 1, -- 状态：1-生效，0-失效
    created_by VARCHAR(50) NOT NULL, -- 创建人
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    updated_by VARCHAR(50) NULL, -- 更新人
    updated_time TIMESTAMP NULL, -- 更新时间
    search_count INTEGER DEFAULT 0, -- 搜索次数
    download_count INTEGER DEFAULT 0, -- 下载次数
    deleted SMALLINT DEFAULT 0 -- 逻辑删除标识(0/1)
);

-- 知识-工作空间 关联表（多对多）
CREATE TABLE knowledge_workspace (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    workspace VARCHAR(50) NOT NULL,
    UNIQUE(knowledge_id, workspace)
);

-- 知识版本表
CREATE TABLE knowledge_versions (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL, -- 知识ID
    version_number INTEGER NOT NULL, -- 版本号
    name VARCHAR(200) NOT NULL, -- 知识名称
    description TEXT, -- 文字描述
    parent_id BIGINT NULL, -- 父知识ID
    node_type VARCHAR(10) DEFAULT 'doc' CHECK (node_type IN ('folder','doc')), -- 节点类型
    tags JSONB, -- 标签列表
    effective_start_time TIMESTAMP NULL, -- 生效开始时间
    effective_end_time TIMESTAMP NULL, -- 生效结束时间
    created_by VARCHAR(50) NOT NULL, -- 创建人
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 创建时间
    status INTEGER DEFAULT 1, -- 状态：1-生效，0-失效
    updated_by VARCHAR(50) NULL, -- 更新人
    updated_time TIMESTAMP NULL, -- 更新时间
    search_count INTEGER DEFAULT 0, -- 搜索次数
    download_count INTEGER DEFAULT 0, -- 下载次数
    change_reason VARCHAR(500) NULL, -- 变更原因
    deleted SMALLINT DEFAULT 0 -- 逻辑删除标识(0/1)
);

-- 附件表
CREATE TABLE attachments (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL, -- 知识ID
    file_name VARCHAR(200) NOT NULL, -- 文件名
    file_path VARCHAR(500) NOT NULL, -- 文件路径
    file_size BIGINT NOT NULL, -- 文件大小(字节)
    file_type VARCHAR(50) NULL, -- 文件类型
    upload_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 上传时间
    file_hash VARCHAR(64) NULL, -- 内容哈希，用于去重
    version_id BIGINT NULL, -- 版本ID
    version_number INTEGER NULL, -- 版本号
    download_count INTEGER DEFAULT 0, -- 下载次数
    deleted BOOLEAN DEFAULT FALSE -- 逻辑删除标识
);

-- 点赞表
CREATE TABLE knowledge_likes (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted SMALLINT DEFAULT 0
);

-- 收藏表
CREATE TABLE knowledge_favorites (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted SMALLINT DEFAULT 0
);

-- 反馈表
CREATE TABLE knowledge_feedbacks (
    id BIGSERIAL PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    feedback_type VARCHAR(20) NULL CHECK (feedback_type IN ('out_of_date','unclear','not_relevant')), -- 反馈类型
    content TEXT NULL,
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted SMALLINT DEFAULT 0
);

-- 搜索历史表
CREATE TABLE search_history (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL, -- 用户ID
    query VARCHAR(500) NOT NULL, -- 搜索关键词
    search_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 搜索时间
    result_count INTEGER NULL, -- 结果数量
    deleted SMALLINT DEFAULT 0 -- 逻辑删除标识(0/1)
);

-- AI回答反馈（针对具体会话与回答消息）
CREATE TABLE chat_feedbacks (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL, -- 会话ID
    message_id VARCHAR(64) NOT NULL, -- 回答消息ID
    user_id BIGINT NOT NULL, -- 用户ID
    attitude VARCHAR(10) NOT NULL CHECK (attitude IN ('like','dislike')), -- 态度：点赞/点踩
    feedback_type VARCHAR(20) NULL CHECK (feedback_type IN ('out_of_date','unclear','not_relevant')), -- 反馈类型
    content TEXT NULL, -- 点踩原因（可空）
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted SMALLINT DEFAULT 0 -- 逻辑删除(0/1)
);

-- RAG会话（持久化）
CREATE TABLE chat_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL UNIQUE, -- 会话ID
    session_name VARCHAR(200) NULL, -- 会话名称
    created_by VARCHAR(50) NOT NULL, -- 创建人
    status VARCHAR(20) DEFAULT 'ACTIVE', -- 状态
    message_count INTEGER DEFAULT 0, -- 消息数量
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_active_time TIMESTAMP NULL
);

-- RAG会话消息（持久化）
CREATE TABLE chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL, -- 会话ID
    message_id VARCHAR(64) NOT NULL UNIQUE, -- 消息ID
    role VARCHAR(10) NOT NULL CHECK (role IN ('user','assistant')), -- 角色
    content TEXT NULL,
    references_json JSONB NULL, -- 引用数据(JSON)
    timestamp_ms BIGINT NOT NULL, -- 时间戳(毫秒)
    created_by VARCHAR(50) NULL -- 创建人（便捷按用户查询）
);

-- 用户部门角色表（保留）
CREATE TABLE user_dept_role (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    dept VARCHAR(50) NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- 工作空间表
CREATE TABLE workspaces (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_knowledge_parent_id ON knowledge(parent_id);
CREATE INDEX idx_knowledge_node_type ON knowledge(node_type);
CREATE INDEX idx_knowledge_created_by ON knowledge(created_by);
CREATE INDEX idx_knowledge_workspace_knowledge_id ON knowledge_workspace(knowledge_id);
CREATE INDEX idx_knowledge_workspace_workspace ON knowledge_workspace(workspace);
CREATE INDEX idx_attachments_knowledge_id ON attachments(knowledge_id);
CREATE INDEX idx_kl_kid ON knowledge_likes(knowledge_id);
CREATE INDEX idx_kf_kid ON knowledge_favorites(knowledge_id);
CREATE INDEX idx_kfb_kid ON knowledge_feedbacks(knowledge_id);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_chat_fb_sess ON chat_feedbacks(session_id);
CREATE INDEX idx_chat_fb_msg ON chat_feedbacks(message_id);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(created_by);
CREATE INDEX idx_chat_sessions_last_active ON chat_sessions(last_active_time);
CREATE INDEX idx_chat_msgs_session ON chat_messages(session_id);
CREATE INDEX idx_chat_msgs_time ON chat_messages(timestamp_ms);
CREATE INDEX idx_ws_code ON workspaces(code);

-- 插入默认数据
INSERT INTO workspaces (code, name, description) VALUES 
('WPB', 'WPB工作空间', 'WPB相关文档'),
('GPB', 'GPB工作空间', 'GPB相关文档'),
('ALL', '全部工作空间', '所有用户可访问');

-- 插入admin用户（密码为 admin123 的BCrypt哈希）
INSERT INTO users (username, staffid, email, system_role, staff_role, workspace, display_name, password) VALUES 
('666666', '666666', 'admin@company.com', 'Admin', 'Admin', 'WPB,GPB', '系统管理员', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iKTVEFDi');

-- 插入测试知识数据
INSERT INTO knowledge (name, description, parent_id, node_type, tags, created_by) VALUES 
('WPB', 'WPB工作空间根目录', 0, 'folder', '[]', '666666'),
('GPB', 'GPB工作空间根目录', 0, 'folder', '[]', '666666');

-- 关联知识到工作空间
INSERT INTO knowledge_workspace (knowledge_id, workspace) VALUES 
(1, 'WPB'),
(2, 'GPB');


-- 切到目标 schema（若连接串已配 currentSchema，可忽略）
SET search_path TO knowledge_base, public;

BEGIN;

-- users
ALTER TABLE IF EXISTS users
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS users
  ADD CONSTRAINT users_deleted_ck CHECK (deleted IN (0,1));

-- knowledge
ALTER TABLE IF EXISTS knowledge
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS knowledge
  ADD CONSTRAINT knowledge_deleted_ck CHECK (deleted IN (0,1));

-- knowledge_versions
ALTER TABLE IF EXISTS knowledge_versions
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS knowledge_versions
  ADD CONSTRAINT knowledge_versions_deleted_ck CHECK (deleted IN (0,1));

-- attachments
ALTER TABLE IF EXISTS attachments
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS attachments
  ADD CONSTRAINT attachments_deleted_ck CHECK (deleted IN (0,1));

-- knowledge_likes
ALTER TABLE IF EXISTS knowledge_likes
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS knowledge_likes
  ADD CONSTRAINT knowledge_likes_deleted_ck CHECK (deleted IN (0,1));

-- knowledge_favorites
ALTER TABLE IF EXISTS knowledge_favorites
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS knowledge_favorites
  ADD CONSTRAINT knowledge_favorites_deleted_ck CHECK (deleted IN (0,1));

-- knowledge_feedbacks
ALTER TABLE IF EXISTS knowledge_feedbacks
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS knowledge_feedbacks
  ADD CONSTRAINT knowledge_feedbacks_deleted_ck CHECK (deleted IN (0,1));

-- search_history
ALTER TABLE IF EXISTS search_history
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS search_history
  ADD CONSTRAINT search_history_deleted_ck CHECK (deleted IN (0,1));

-- chat_feedbacks（若有）
ALTER TABLE IF EXISTS chat_feedbacks
  ALTER COLUMN deleted DROP DEFAULT,
  ALTER COLUMN deleted TYPE SMALLINT USING (CASE WHEN deleted IS TRUE THEN 1 WHEN deleted IS FALSE THEN 0 ELSE 0 END),
  ALTER COLUMN deleted SET DEFAULT 0;
ALTER TABLE IF EXISTS chat_feedbacks
  ADD CONSTRAINT chat_feedbacks_deleted_ck CHECK (deleted IN (0,1));

-- categories / attachment_versions / category_change_log 等如存在也同样处理：
-- ALTER TABLE IF EXISTS categories ...（同上模板）
-- ALTER TABLE IF EXISTS attachment_versions ...
-- ALTER TABLE IF EXISTS category_change_log ...

COMMIT;