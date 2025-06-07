CREATE TABLE `message_info`  (
  `database_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `message_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `message_context` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `group_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `user_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `time` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

CREATE TABLE `user_info_new`  (
  `user_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `user_coin` int NULL DEFAULT NULL,
  `user_health` int NULL DEFAULT NULL,
  `user_crime` int NULL DEFAULT NULL,
  `user_coin_max` int NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

CREATE TABLE `user_info`  (
  `user_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `user_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `sign_time` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `last_speak_time` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `speak_time_total` int NULL DEFAULT NULL,
  `coin` double NULL DEFAULT NULL
) ENGINE = InnoDB AUTO_INCREMENT = 30114 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

CREATE TABLE `message_info` (
  `database_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `message_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `message_context` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `group_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `user_id` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `time` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 ROW_FORMAT=DYNAMIC;


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