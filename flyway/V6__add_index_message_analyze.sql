-- 消息分析表索引优化脚本

-- 删除现有索引（如果需要重建的话）
-- ALTER TABLE message_analyze DROP INDEX idx_name;

-- 添加主查询索引
ALTER TABLE message_analyze ADD INDEX idx_main_query (
    user_id, 
    group_id, 
    key_word, 
    is_deleted
);

-- 添加统计查询索引
ALTER TABLE message_analyze ADD INDEX idx_stats_query (
    group_id, 
    is_deleted, 
    key_word
);

-- 添加时间范围查询索引
ALTER TABLE message_analyze ADD INDEX idx_time_query (
    group_id, 
    create_time, 
    is_deleted, 
    key_word
);

-- 添加用户查询索引
ALTER TABLE message_analyze ADD INDEX idx_user_query (
    user_id, 
    group_id, 
    is_deleted
);

-- 添加更新时间索引（用于监控）
ALTER TABLE message_analyze ADD INDEX idx_update_time (update_time);

-- 添加关键词索引
ALTER TABLE message_analyze ADD INDEX idx_key_word (
    key_word
);