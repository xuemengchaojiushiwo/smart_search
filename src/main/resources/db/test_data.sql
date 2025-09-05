-- 测试数据SQL：用户、workspace、知识关联关系
-- 执行前请确保已运行 init_fixed.sql

USE knowledge_base;

-- 1. 插入测试用户（都关联WPB workspace）
INSERT INTO users (staffid, username, email, role, system_role, staff_role, workspace, status, created_time, updated_time) VALUES
('001', 'admin', 'admin@wpb.com', 'ADMIN', 'ADMIN', 'Manager', 'WPB', 1, NOW(), NOW()),
('002', 'reviewer1', 'reviewer1@wpb.com', 'USER', 'REVIEWER', 'Senior', 'WPB', 1, NOW(), NOW()),
('003', 'reviewer2', 'reviewer2@wpb.com', 'USER', 'REVIEWER', 'Senior', 'WPB', 1, NOW(), NOW()),
('004', 'user1', 'user1@wpb.com', 'USER', 'USER', 'Staff', 'WPB', 1, NOW(), NOW()),
('005', 'user2', 'user2@wpb.com', 'USER', 'USER', 'Staff', 'WPB', 1, NOW(), NOW()),
('006', 'blocked_user', 'blocked@wpb.com', 'USER', 'BLOCKED', 'Staff', 'WPB', 1, NOW(), NOW())
ON DUPLICATE KEY UPDATE 
    workspace = VALUES(workspace),
    system_role = VALUES(system_role),
    updated_time = NOW();

-- 2. 插入用户部门角色关系（使用WPB作为部门）
INSERT INTO user_dept_role (user_id, dept, role) VALUES
((SELECT id FROM users WHERE staffid = '001'), 'WPB', 'ADMIN'),
((SELECT id FROM users WHERE staffid = '002'), 'WPB', 'REVIEWER'),
((SELECT id FROM users WHERE staffid = '003'), 'WPB', 'REVIEWER'),
((SELECT id FROM users WHERE staffid = '004'), 'WPB', 'USER'),
((SELECT id FROM users WHERE staffid = '005'), 'WPB', 'USER'),
((SELECT id FROM users WHERE staffid = '006'), 'WPB', 'BLOCKED')
ON DUPLICATE KEY UPDATE 
    role = VALUES(role);

-- 3. 插入测试知识（层级结构：类目folder + 文档doc）
INSERT INTO knowledge (name, description, parent_id, node_type, tags, status, created_by, created_time, updated_time, search_count, download_count) VALUES
-- 根类目
('制度管理', '公司各类制度文档的管理与维护', NULL, 'folder', '["制度","管理"]', 1, 'admin', NOW(), NOW(), 0, 0),
('技术文档', '技术相关文档与规范', NULL, 'folder', '["技术","文档"]', 1, 'admin', NOW(), NOW(), 0, 0),
('培训资料', '员工培训与学习资料', NULL, 'folder', '["培训","学习"]', 1, 'admin', NOW(), NOW(), 0, 0),

-- 制度管理下的文档
('员工手册V2.1', '最新版员工手册，包含行为规范、福利制度等', (SELECT id FROM knowledge WHERE name = '制度管理' AND node_type = 'folder'), 'doc', '["员工","手册","规范"]', 1, 'reviewer1', NOW(), NOW(), 15, 3),
('请假制度', '员工请假流程与审批规定', (SELECT id FROM knowledge WHERE name = '制度管理' AND node_type = 'folder'), 'doc', '["请假","流程","HR"]', 1, 'reviewer1', NOW(), NOW(), 8, 1),
('差旅报销制度', '出差费用报销标准与流程', (SELECT id FROM knowledge WHERE name = '制度管理' AND node_type = 'folder'), 'doc', '["差旅","报销","财务"]', 1, 'reviewer2', NOW(), NOW(), 12, 5),

-- 技术文档下的文档
('Java开发规范', 'Java代码开发规范与最佳实践', (SELECT id FROM knowledge WHERE name = '技术文档' AND node_type = 'folder'), 'doc', '["Java","开发","规范"]', 1, 'admin', NOW(), NOW(), 25, 8),
('数据库设计规范', '数据库表结构设计与命名规范', (SELECT id FROM knowledge WHERE name = '技术文档' AND node_type = 'folder'), 'doc', '["数据库","设计","规范"]', 1, 'admin', NOW(), NOW(), 18, 4),
('API接口文档', 'RESTful API设计规范与接口文档', (SELECT id FROM knowledge WHERE name = '技术文档' AND node_type = 'folder'), 'doc', '["API","接口","RESTful"]', 1, 'reviewer1', NOW(), NOW(), 22, 6),

-- 培训资料下的文档
('新员工入职指南', '新员工入职流程与注意事项', (SELECT id FROM knowledge WHERE name = '培训资料' AND node_type = 'folder'), 'doc', '["新员工","入职","指南"]', 1, 'reviewer2', NOW(), NOW(), 35, 12),
('安全培训手册', '信息安全与办公安全培训材料', (SELECT id FROM knowledge WHERE name = '培训资料' AND node_type = 'folder'), 'doc', '["安全","培训","信息安全"]', 1, 'admin', NOW(), NOW(), 28, 9);

-- 4. 将所有知识与WPB workspace关联
INSERT INTO knowledge_workspace (knowledge_id, workspace)
SELECT id, 'WPB' FROM knowledge
ON DUPLICATE KEY UPDATE workspace = VALUES(workspace);

-- 5. 插入一些测试附件记录（模拟已上传的文档）
INSERT INTO attachments (knowledge_id, file_name, file_path, file_size, file_type, upload_time, uploaded_by, download_count) VALUES
((SELECT id FROM knowledge WHERE name = '员工手册V2.1'), '员工手册V2.1.pdf', '/uploads/employee_handbook_v2.1.pdf', 2048576, 'pdf', NOW(), 'reviewer1', 3),
((SELECT id FROM knowledge WHERE name = '请假制度'), '请假申请流程图.png', '/uploads/leave_process.png', 512000, 'png', NOW(), 'reviewer1', 1),
((SELECT id FROM knowledge WHERE name = '差旅报销制度'), '差旅报销表格.xlsx', '/uploads/travel_expense_form.xlsx', 256000, 'xlsx', NOW(), 'reviewer2', 5),
((SELECT id FROM knowledge WHERE name = 'Java开发规范'), 'Java编码规范.md', '/uploads/java_coding_standards.md', 128000, 'md', NOW(), 'admin', 8),
((SELECT id FROM knowledge WHERE name = 'API接口文档'), 'API文档v1.2.json', '/uploads/api_docs_v1.2.json', 64000, 'json', NOW(), 'reviewer1', 6),
((SELECT id FROM knowledge WHERE name = '新员工入职指南'), '入职checklist.docx', '/uploads/onboarding_checklist.docx', 384000, 'docx', NOW(), 'reviewer2', 12);

-- 6. 插入一些搜索历史记录
INSERT INTO search_history (user_id, query, result_count, search_time) VALUES
((SELECT id FROM users WHERE staffid = '004'), '请假流程', 2, DATE_SUB(NOW(), INTERVAL 1 DAY)),
((SELECT id FROM users WHERE staffid = '004'), 'Java规范', 1, DATE_SUB(NOW(), INTERVAL 2 HOUR)),
((SELECT id FROM users WHERE staffid = '005'), '员工手册', 1, DATE_SUB(NOW(), INTERVAL 3 HOUR)),
((SELECT id FROM users WHERE staffid = '005'), '报销制度', 1, DATE_SUB(NOW(), INTERVAL 1 HOUR)),
((SELECT id FROM users WHERE staffid = '002'), 'API文档', 1, DATE_SUB(NOW(), INTERVAL 30 MINUTE));

-- 7. 验证数据插入结果
SELECT '=== 用户信息 ===' as info;
SELECT id, staffid, username, workspace, system_role FROM users WHERE deleted = 0;

SELECT '=== 知识结构 ===' as info;
SELECT k.id, k.name, k.node_type, k.parent_id, 
       COALESCE(p.name, 'ROOT') as parent_name,
       GROUP_CONCAT(kw.workspace) as workspaces
FROM knowledge k 
LEFT JOIN knowledge p ON k.parent_id = p.id
LEFT JOIN knowledge_workspace kw ON k.id = kw.knowledge_id
WHERE k.deleted = 0
GROUP BY k.id, k.name, k.node_type, k.parent_id, p.name
ORDER BY k.parent_id, k.node_type, k.name;

SELECT '=== Workspace关联统计 ===' as info;
SELECT workspace, COUNT(*) as knowledge_count 
FROM knowledge_workspace kw
JOIN knowledge k ON kw.knowledge_id = k.id
WHERE k.deleted = 0
GROUP BY workspace;

-- 完成提示
SELECT '测试数据插入完成！' as status,
       (SELECT COUNT(*) FROM users WHERE deleted = 0) as user_count,
       (SELECT COUNT(*) FROM knowledge WHERE deleted = 0) as knowledge_count,
       (SELECT COUNT(*) FROM knowledge_workspace) as workspace_binding_count;
