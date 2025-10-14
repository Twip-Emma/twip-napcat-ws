-- 加主键
ALTER TABLE `message_info` 
ADD COLUMN `id` BIGINT AUTO_INCREMENT PRIMARY KEY FIRST;

-- 为 message_id 添加索引
ALTER TABLE `message_info` ADD INDEX `idx_message_id` (`message_id`);

-- 为 group_id 添加索引  
ALTER TABLE `message_info` ADD INDEX `idx_group_id` (`group_id`);

-- 为 user_id 添加索引
ALTER TABLE `message_info` ADD INDEX `idx_user_id` (`user_id`);



