'''
Author: 七画一只妖
Date: 2022-02-14 12:12:53
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-06-07 11:24:13
Description: file content
'''

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import (Bot, GroupMessageEvent,
                                         GroupRecallNoticeEvent, MessageEvent,
                                         MessageSegment)
from nonebot.plugin import PluginMetadata
from tool.utils import message_utils
import json
from tool.utils import db

# __plugin_meta__ = PluginMetadata(
#     name='静默者-闪照撤回',
#     description='功能：破解闪照、破解撤回',
#     usage='''使用方式：无【静默模块】''',
#     extra={'version': 'v1.0.1',
#            'cost': '无消耗'}
# )

recall_matcher = on_notice(priority=10, block=True)

@recall_matcher.handle()
async def _(bot: Bot, event: GroupRecallNoticeEvent):
    # 确保只处理群撤回事件
    if event.notice_type != "group_recall":
        return
    
    try:
        sql2 = """
            SELECT message_context FROM message_info WHERE message_id = %s ORDER BY time DESC
        """
        data = db.sql_dql(sql2, (str(event.message_id),))
        
        # 插入数据库
        recall_data = {
            'message_id': event.message_id,
            'group_id': event.group_id,
            'user_id': event.user_id,
            'operator_id': event.operator_id,
            'recall_time': event.time,
            'message_content': data[0][0],
            'message_type': 'text',  # 这里可以根据实际消息类型调整
            'bot_id': event.self_id,
        }
        sql = """
            INSERT INTO group_recall_records 
            (message_id, group_id, user_id, operator_id, recall_time, message_content, message_type, bot_id)
            VALUES (%(message_id)s, %(group_id)s, %(user_id)s, %(operator_id)s, %(recall_time)s, 
                    %(message_content)s, %(message_type)s, %(bot_id)s)
            """
        db.sql_dml(sql, recall_data)
    except Exception as e:
        # 记录错误日志
        print(f"记录撤回消息失败: {e}")