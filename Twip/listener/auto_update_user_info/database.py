'''
Author: 七画一只妖
Date: 2022-01-22 21:42:16
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-06-07 11:50:10
Description: file content
'''
import MySQLdb
import datetime
import re
import uuid

from tool.utils import db


def insert_new_user(user_name, user_id, now_time) -> None:
    sql = "INSERT INTO user_info VALUES(%s, %s, %s, %s, %s, %s)"
    args = (f'{user_name}', f'{user_id}',
            f"{now_time}", f"{now_time}", "0", "0")
    args2 = (get_real_name(user_name=user_name), f'{user_id}',
            f"{now_time}", f"{now_time}", "0", "0")
    try:
        db.sql_dml(sql, args)
    except:
        db.sql_dml(sql, args2)


# 老用户修改即可
def change_speak_total(user_id: str) -> None:
    sql = "UPDATE user_info SET speak_time_total=speak_time_total+1 WHERE user_id=%s;"
    db.sql_dml(sql, (str(user_id),))

# 修改昵称
def change_name(user_id: str, user_name: str) -> None:
    user_name = re.findall(r'[\u4e00-\u9fa5]', user_name)
    user_name = "".join(user_name)
    sql = "UPDATE user_info SET user_name=%s WHERE user_id=%s;"
    db.sql_dml(sql, (user_name, user_id))

# 修改上次发言时间
def change_sign_time(user_id: str, now_time: str) -> None:
    sql = "UPDATE user_info SET last_speak_time= %s WHERE user_id= %s;"
    db.sql_dml(sql, (now_time, user_id))

# 判断用户是否存在
def chack_user(user_id: str) -> bool:
    sql = "SELECT * FROM user_info WHERE user_id=%s;"
    user = db.sql_dql(sql, (user_id,))
    if user:
        return user


# 总控
def start(user_name: str, user_id: str) -> None:
    re = chack_user(user_id=user_id)
    now_time = datetime.datetime.now().strftime('%Y-%m-%d')
    if re:
        user_data = re[0]
        if now_time != user_data[3]:
            change_sign_time(now_time=now_time, user_id=user_id)
            change_speak_total(user_id=user_id)
        else:
            change_speak_total(user_id=user_id)
    else:
        try:
            insert_new_user(user_name=user_name,user_id=user_id, now_time=now_time)
        except:
            insert_new_user(user_name=user_id,user_id=user_id, now_time=now_time)



    # 记录每日发言 t_bot_listener_speaklog
    sql = "SELECT * FROM t_bot_listener_speaklog WHERE user_id=%s and speak_time=%s;"
    results = db.sql_dql(sql, (user_id, now_time))
    if not results:
        sql = "INSERT INTO t_bot_listener_speaklog(id, user_id, user_name, speak_time, speak_count) VALUES (%s, %s, %s, %s, %s);"
        try:
            db.sql_dml(sql, (uuid.uuid1(), user_id, user_name, now_time, 1))
        except:
            db.sql_dml(sql, (uuid.uuid1(), user_id, get_real_name(user_name), now_time, 1))
    else:
        sql = "UPDATE t_bot_listener_speaklog SET speak_count=speak_count+1 WHERE user_id=%s and speak_time=%s;"
        db.sql_dml(sql, (user_id, now_time))


# 获取处理后的昵称
def get_real_name(user_name:str) -> str:
    user_name = re.findall(r'[\u4e00-\u9fa5]', user_name) # 使用通配符只匹配汉字
    user_name = "".join(user_name)
    return user_name