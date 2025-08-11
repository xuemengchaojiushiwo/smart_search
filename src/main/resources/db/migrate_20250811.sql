-- 数据库迁移脚本：补齐知识版本表与附件表缺失字段（2025-08-11）
-- 注意：在Windows PowerShell中逐条执行每个命令（不要用 &&）。

USE knowledge_base;

-- 1) knowledge_versions 表补齐字段
-- 说明：根据实体 `KnowledgeVersion`，需要以下字段
-- 可能已有的字段：id, knowledge_id, version_number, name, description, category_id, tags, effective_start_time,
--                 effective_end_time, created_by, created_time, change_reason, deleted
-- 需要补齐：status, updated_by, updated_time, search_count, download_count

ALTER TABLE knowledge_versions ADD COLUMN status TINYINT DEFAULT 1 COMMENT '状态：1-生效，0-失效';
ALTER TABLE knowledge_versions ADD COLUMN updated_by VARCHAR(50) COMMENT '更新人';
ALTER TABLE knowledge_versions ADD COLUMN updated_time DATETIME COMMENT '更新时间';
ALTER TABLE knowledge_versions ADD COLUMN search_count INT DEFAULT 0 COMMENT '搜索次数';
ALTER TABLE knowledge_versions ADD COLUMN download_count INT DEFAULT 0 COMMENT '下载次数';

-- 2) attachments 表补齐字段
-- 目标结构包含：id, knowledge_id, file_name, file_path, file_size, file_type, file_hash, version_id,
--              version_number, upload_time, download_count, deleted

ALTER TABLE attachments ADD COLUMN file_name VARCHAR(200) NOT NULL COMMENT '文件名' AFTER knowledge_id;
ALTER TABLE attachments ADD COLUMN file_path VARCHAR(500) NOT NULL COMMENT '文件路径' AFTER file_name;
ALTER TABLE attachments ADD COLUMN file_size BIGINT NOT NULL COMMENT '文件大小(字节)' AFTER file_path;
ALTER TABLE attachments ADD COLUMN file_type VARCHAR(50) COMMENT '文件类型' AFTER file_size;
ALTER TABLE attachments ADD COLUMN file_hash VARCHAR(64) COMMENT '文件内容哈希' AFTER file_type;
ALTER TABLE attachments ADD COLUMN version_id BIGINT COMMENT '关联的知识版本ID' AFTER file_hash;
ALTER TABLE attachments ADD COLUMN version_number INT COMMENT '版本号' AFTER version_id;
ALTER TABLE attachments ADD COLUMN upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间' AFTER version_number;
ALTER TABLE attachments ADD COLUMN download_count INT DEFAULT 0 COMMENT '下载次数' AFTER upload_time;

-- 提示：若执行报 Duplicate column name，表示该列已存在，可忽略该错误继续执行后续语句。



