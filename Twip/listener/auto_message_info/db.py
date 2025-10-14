'''
Author: 七画一只妖
Date: 2021-11-09 20:03:46
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-06-07 11:29:43
Description: file content
'''
import MySQLdb
import uuid
import datetime

from tool.utils import db


def insert_into_sql(message_id, message_context, group_id, user_id):
    uid = uuid.uuid1()
    now_time = datetime.datetime.now()
    now_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        sql = "INSERT INTO message_info (database_id, message_id, message_context, group_id, user_id, time)VALUES(%s, %s, %s, %s, %s, %s)"
        args = (f'{uid}', f'{message_id}', f"{message_context}",
                f"{group_id}", f"{user_id}", f"{now_time}")
        db.sql_dml(sql, args)
    except:
        sql = "INSERT INTO message_info (database_id, message_id, message_context, group_id, user_id, time)VALUES(%s, %s, %s, %s, %s, %s)"
        args = (f'{uid}', f'{message_id}', '消息太长了，这是个xml卡片或者分享链接',
                f"{group_id}", f"{user_id}", f"{now_time}")
        db.sql_dml(sql, args)