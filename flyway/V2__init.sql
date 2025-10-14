CREATE TABLE `group_recall_records` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `message_id` bigint NOT NULL COMMENT '被撤回消息的原始ID',
  `group_id` bigint NOT NULL COMMENT '群号',
  `user_id` bigint NOT NULL COMMENT '被撤回消息的发送者QQ号',
  `operator_id` bigint NOT NULL COMMENT '撤回操作执行者QQ号',
  `recall_time` int NOT NULL COMMENT '撤回时间戳',
  `message_content` text COMMENT '被撤回的消息内容(原始JSON或解析后的文本)',
  `message_type` varchar(20) DEFAULT NULL COMMENT '消息类型(text/image/etc)',
  `bot_id` bigint NOT NULL COMMENT '机器人QQ号',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='QQ群消息撤回记录表';