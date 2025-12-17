CREATE TABLE message_analyze (
    id           BIGINT UNSIGNED auto_increment PRIMARY KEY COMMENT '主键',
    create_time  datetime             DEFAULT NULL COMMENT '创建时间',
    update_time  datetime             DEFAULT NULL COMMENT '更新时间',
    is_deleted   boolean     NOT NULL DEFAULT FALSE COMMENT '是否删除',
    is_sensitive boolean     NOT NULL DEFAULT FALSE COMMENT '是否敏感数据',

    user_id VARCHAR(30) NOT NULL COMMENT '用户ID',
    group_id VARCHAR(30) NOT NULL COMMENT '群号',
    key_word VARCHAR(10) NOT NULL COMMENT '关键词',
    count int NOT NULL DEFAULT 0 COMMENT '次数'
) COMMENT='消息分词表';