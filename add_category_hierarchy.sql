-- 添加6层category层级结构的SQL脚本
-- 执行前请确保categories表已存在

-- 清空现有数据（可选，谨慎使用）
-- DELETE FROM categories WHERE deleted = 0;

-- 第1层：技术文档
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('技术文档', '各类技术文档和资料', NULL, 1, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第2层：开发技术
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('开发技术', '软件开发相关技术文档', 1, 2, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第3层：编程语言
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('编程语言', '各种编程语言相关文档', 2, 3, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第4层：Java开发
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('Java开发', 'Java编程语言相关文档', 3, 4, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第5层：Spring框架
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('Spring框架', 'Spring框架相关文档和教程', 4, 5, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第6层：Spring Boot
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('Spring Boot', 'Spring Boot微服务框架文档', 5, 6, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 添加另一个6层分支：数据库技术
-- 第2层：数据库技术
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('数据库技术', '数据库相关技术文档', 1, 2, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第3层：关系型数据库
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('关系型数据库', '关系型数据库相关文档', 8, 3, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第4层：MySQL
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('MySQL', 'MySQL数据库相关文档', 9, 4, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第5层：MySQL优化
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('MySQL优化', 'MySQL性能优化相关文档', 10, 5, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第6层：索引优化
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('索引优化', 'MySQL索引优化技术文档', 11, 6, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 添加第三个6层分支：运维技术
-- 第2层：运维技术
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('运维技术', '系统运维相关技术文档', 1, 2, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第3层：容器技术
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('容器技术', '容器化技术相关文档', 13, 3, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第4层：Docker
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('Docker', 'Docker容器技术文档', 14, 4, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第5层：Docker部署
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('Docker部署', 'Docker应用部署相关文档', 15, 5, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 第6层：微服务部署
INSERT INTO categories (name, description, parent_id, level, status, created_by, updated_by, created_time, updated_time, deleted) 
VALUES ('微服务部署', 'Docker微服务部署技术文档', 16, 6, 1, 'admin', 'admin', NOW(), NOW(), 0);

-- 验证插入结果
SELECT 
    c1.id as level1_id, c1.name as level1_name,
    c2.id as level2_id, c2.name as level2_name,
    c3.id as level3_id, c3.name as level3_name,
    c4.id as level4_id, c4.name as level4_name,
    c5.id as level5_id, c5.name as level5_name,
    c6.id as level6_id, c6.name as level6_name
FROM categories c1
LEFT JOIN categories c2 ON c2.parent_id = c1.id
LEFT JOIN categories c3 ON c3.parent_id = c2.id
LEFT JOIN categories c4 ON c4.parent_id = c3.id
LEFT JOIN categories c5 ON c5.parent_id = c4.id
LEFT JOIN categories c6 ON c6.parent_id = c5.id
WHERE c1.level = 1 AND c1.deleted = 0
ORDER BY c1.id, c2.id, c3.id, c4.id, c5.id, c6.id; 