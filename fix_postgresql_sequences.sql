-- PostgreSQL 序列修复脚本
-- 用于修复数据迁移后的序列值，避免 duplicate key 错误

-- 修复所有表的序列值
DO $$
DECLARE
    table_name TEXT;
    sequence_name TEXT;
    max_id BIGINT;
    next_val BIGINT;
    table_sequences TEXT[][] := ARRAY[
        ['knowledge', 'knowledge_id_seq'],
        ['users', 'users_id_seq'],
        ['attachments', 'attachments_id_seq'],
        ['knowledge_versions', 'knowledge_versions_id_seq'],
        ['knowledge_history_versions', 'knowledge_history_versions_id_seq'],
        ['knowledge_workspace', 'knowledge_workspace_id_seq'],
        ['knowledge_likes', 'knowledge_likes_id_seq'],
        ['knowledge_favorites', 'knowledge_favorites_id_seq'],
        ['knowledge_feedbacks', 'knowledge_feedbacks_id_seq'],
        ['search_history', 'search_history_id_seq'],
        ['chat_feedbacks', 'chat_feedbacks_id_seq'],
        ['chat_sessions', 'chat_sessions_id_seq'],
        ['chat_messages', 'chat_messages_id_seq']
    ];
BEGIN
    RAISE NOTICE '开始修复PostgreSQL序列...';
    
    -- 遍历所有表和序列
    FOR i IN 1..array_length(table_sequences, 1) LOOP
        table_name := table_sequences[i][1];
        sequence_name := table_sequences[i][2];
        
        BEGIN
            -- 获取表中当前最大的ID
            EXECUTE format('SELECT COALESCE(MAX(id), 0) FROM %I', table_name) INTO max_id;
            
            -- 设置序列的下一个值
            next_val := max_id + 1;
            EXECUTE format('SELECT setval(%L, %s, false)', sequence_name, next_val);
            
            RAISE NOTICE '%: 最大ID=%, 序列设置为=%', table_name, max_id, next_val;
            
        EXCEPTION WHEN OTHERS THEN
            RAISE WARNING '修复表 % 的序列失败: %', table_name, SQLERRM;
            -- 继续处理其他表
        END;
    END LOOP;
    
    RAISE NOTICE '序列修复完成！';
    
    -- 验证序列状态
    RAISE NOTICE '验证序列状态:';
    FOR i IN 1..array_length(table_sequences, 1) LOOP
        table_name := table_sequences[i][1];
        sequence_name := table_sequences[i][2];
        
        BEGIN
            EXECUTE format('SELECT last_value FROM %I', sequence_name) INTO next_val;
            RAISE NOTICE '  %: %', sequence_name, next_val;
        EXCEPTION WHEN OTHERS THEN
            RAISE WARNING '获取序列 % 状态失败: %', sequence_name, SQLERRM;
        END;
    END LOOP;
    
END $$;

-- 单独修复特定表的序列（如果需要）
-- 示例：修复 knowledge 表的序列
/*
DO $$
DECLARE
    max_id BIGINT;
    next_val BIGINT;
BEGIN
    -- 获取 knowledge 表的最大ID
    SELECT COALESCE(MAX(id), 0) INTO max_id FROM knowledge;
    
    -- 设置序列的下一个值
    next_val := max_id + 1;
    PERFORM setval('knowledge_id_seq', next_val, false);
    
    RAISE NOTICE 'knowledge: 最大ID=%, 序列设置为=%', max_id, next_val;
END $$;
*/

-- 检查序列状态的查询
/*
SELECT 
    schemaname,
    sequencename,
    last_value,
    start_value,
    increment_by,
    max_value,
    min_value,
    cache_value,
    is_cycled
FROM pg_sequences 
WHERE sequencename LIKE '%_seq'
ORDER BY sequencename;
*/

-- 检查表的最大ID和对应序列值的对比
/*
SELECT 
    'knowledge' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM knowledge) as max_id,
    (SELECT last_value FROM knowledge_id_seq) as seq_value
UNION ALL
SELECT 
    'users' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM users) as max_id,
    (SELECT last_value FROM users_id_seq) as seq_value
UNION ALL
SELECT 
    'attachments' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM attachments) as max_id,
    (SELECT last_value FROM attachments_id_seq) as seq_value
UNION ALL
SELECT 
    'knowledge_versions' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM knowledge_versions) as max_id,
    (SELECT last_value FROM knowledge_versions_id_seq) as seq_value
UNION ALL
SELECT 
    'knowledge_history_versions' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM knowledge_history_versions) as max_id,
    (SELECT last_value FROM knowledge_history_versions_id_seq) as seq_value
UNION ALL
SELECT 
    'knowledge_workspace' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM knowledge_workspace) as max_id,
    (SELECT last_value FROM knowledge_workspace_id_seq) as seq_value
UNION ALL
SELECT 
    'knowledge_likes' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM knowledge_likes) as max_id,
    (SELECT last_value FROM knowledge_likes_id_seq) as seq_value
UNION ALL
SELECT 
    'knowledge_favorites' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM knowledge_favorites) as max_id,
    (SELECT last_value FROM knowledge_favorites_id_seq) as seq_value
UNION ALL
SELECT 
    'knowledge_feedbacks' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM knowledge_feedbacks) as max_id,
    (SELECT last_value FROM knowledge_feedbacks_id_seq) as seq_value
UNION ALL
SELECT 
    'search_history' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM search_history) as max_id,
    (SELECT last_value FROM search_history_id_seq) as seq_value
UNION ALL
SELECT 
    'chat_feedbacks' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM chat_feedbacks) as max_id,
    (SELECT last_value FROM chat_feedbacks_id_seq) as seq_value
UNION ALL
SELECT 
    'chat_sessions' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM chat_sessions) as max_id,
    (SELECT last_value FROM chat_sessions_id_seq) as seq_value
UNION ALL
SELECT 
    'chat_messages' as table_name,
    (SELECT COALESCE(MAX(id), 0) FROM chat_messages) as max_id,
    (SELECT last_value FROM chat_messages_id_seq) as seq_value
ORDER BY table_name;
*/
