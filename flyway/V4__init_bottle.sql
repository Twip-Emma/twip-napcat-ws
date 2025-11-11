DROP TABLE IF EXISTS `bottle_info`;
CREATE TABLE bottle_info (
    id           BIGINT UNSIGNED auto_increment PRIMARY KEY COMMENT '主键',
    create_time  datetime             DEFAULT NULL COMMENT '创建时间',
    update_time  datetime             DEFAULT NULL COMMENT '更新时间',
    is_deleted   boolean     NOT NULL DEFAULT FALSE COMMENT '是否删除',
    is_sensitive boolean     NOT NULL DEFAULT FALSE COMMENT '是否敏感数据',

    user_id VARCHAR(30) NOT NULL COMMENT '用户ID',
    content TEXT NOT NULL COMMENT '漂流瓶内容'
) COMMENT='漂流瓶表';


DROP TABLE IF EXISTS `bottle_img`;
CREATE TABLE bottle_img (
    id           BIGINT UNSIGNED auto_increment PRIMARY KEY COMMENT '主键',
    create_time  datetime             DEFAULT NULL COMMENT '创建时间',
    update_time  datetime             DEFAULT NULL COMMENT '更新时间',
    is_deleted   boolean     NOT NULL DEFAULT FALSE COMMENT '是否删除',
    is_sensitive boolean     NOT NULL DEFAULT FALSE COMMENT '是否敏感数据',

    file_path VARCHAR(200) NOT NULL COMMENT '文件路径',
) COMMENT='漂流瓶-图片关联表';


