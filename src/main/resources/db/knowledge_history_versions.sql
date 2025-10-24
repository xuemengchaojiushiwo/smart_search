-- 知识历史版本表 - 存储每个版本的完整信息
CREATE TABLE IF NOT EXISTS knowledge_history_versions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    version_number INTEGER NOT NULL,
    version_name VARCHAR(50) NOT NULL, -- 如 V1, V2, V3 等
    
    -- 知识基本信息
    name VARCHAR(200) NOT NULL,
    description TEXT,
    parent_id BIGINT,
    node_type VARCHAR(50),
    tags JSONB,
    effective_start_time TIMESTAMP,
    effective_end_time TIMESTAMP,
    status SMALLINT DEFAULT 1,
    
    -- 统计信息
    search_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,
    
    -- 版本管理信息
    change_type VARCHAR(50) NOT NULL, -- CREATE, UPDATE, DELETE
    change_reason VARCHAR(500),
    change_summary TEXT, -- 变更摘要
    
    -- 字段变更详情（JSON格式存储具体变更）
    field_changes JSONB, -- 存储具体哪些字段发生了变化
    
    -- 审计信息
    created_by VARCHAR(50) NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(50),
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 逻辑删除
    deleted SMALLINT DEFAULT 0,
    
    -- 外键约束
    CONSTRAINT fk_knowledge_history_versions_knowledge_id 
        FOREIGN KEY (knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE,
    
    -- 唯一约束
    CONSTRAINT uk_knowledge_history_version 
        UNIQUE (knowledge_id, version_number),
    
    -- 索引
    INDEX idx_knowledge_history_versions_knowledge_id (knowledge_id),
    INDEX idx_knowledge_history_versions_version_number (version_number),
    INDEX idx_knowledge_history_versions_created_time (created_time)
);

-- 添加注释
COMMENT ON TABLE knowledge_history_versions IS '知识历史版本表';
COMMENT ON COLUMN knowledge_history_versions.knowledge_id IS '知识ID';
COMMENT ON COLUMN knowledge_history_versions.version_number IS '版本号（数字）';
COMMENT ON COLUMN knowledge_history_versions.version_name IS '版本名称（如V1, V2等）';
COMMENT ON COLUMN knowledge_history_versions.change_type IS '变更类型：CREATE-创建, UPDATE-更新, DELETE-删除';
COMMENT ON COLUMN knowledge_history_versions.change_reason IS '变更原因';
COMMENT ON COLUMN knowledge_history_versions.change_summary IS '变更摘要';
COMMENT ON COLUMN knowledge_history_versions.field_changes IS '字段变更详情（JSON格式）';
