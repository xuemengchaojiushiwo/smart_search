-- 知识描述版本表
-- 用于记录知识描述的修改历史

CREATE TABLE IF NOT EXISTS knowledge_description_versions (
    id BIGINT PRIMARY KEY,
    knowledge_id BIGINT NOT NULL,
    version VARCHAR(50) NOT NULL,  -- 版本号，如 'V1', 'V2', '2024-01-15' 等
    content TEXT NOT NULL,  -- 版本内容（HTML格式）
    editor VARCHAR(100) NOT NULL,  -- 修改人（用户名）
    editor_id BIGINT,  -- 修改人ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    created_by VARCHAR(100),  -- 创建人
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    updated_by VARCHAR(100),  -- 更新人
    deleted SMALLINT DEFAULT 0,  -- 逻辑删除：0-未删除，1-已删除
    
    -- 索引
    INDEX idx_knowledge_id (knowledge_id),
    INDEX idx_version (version),
    INDEX idx_editor (editor),
    INDEX idx_created_at (created_at),
    
    -- 唯一约束：同一知识同一版本只能有一条记录
    UNIQUE KEY uk_knowledge_version (knowledge_id, version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识描述版本表';

-- 在知识表更新时自动创建版本记录（通过应用层实现，不在这里写触发器）





