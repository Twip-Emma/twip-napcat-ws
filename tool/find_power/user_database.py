'''
Author: 七画一只妖 1157529280@qq.com
Date: 2022-10-10 12:52:51
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-06-07 12:06:32
'''
from typing import Optional, Tuple, Union
from tool.utils import db

# 链接
# db = MySQLdb.connect(DB_URL, DB_CARD, DB_PASS, DB_LIB, charset='utf8')

# 查询user_info_new表指定user_id的记录
# def get_user_info_new(user_id: str) -> tuple:
#     db = MySQLdb.connect(DB_URL, DB_CARD, DB_PASS, DB_LIB, charset='utf8')
#     cursor = db.cursor()
#     sql = f"select * from user_info_new where user_id='{user_id}'"
#     cursor.execute(sql)
#     data = cursor.fetchone()
#     db.close()
#     return data


# # 查询user_info表指定user_id的记录(老表)
# def get_user_info_old(user_id: str) -> tuple:
#     db = MySQLdb.connect(DB_URL, DB_CARD, DB_PASS, DB_LIB, charset='utf8')
#     cursor = db.cursor()
#     sql = f"select * from user_info where user_id='{user_id}'"
#     cursor.execute(sql)
#     data = cursor.fetchone()
#     db.close()
#     return data


# # 向user_info_new表中插入数据
# def insert_user_info_new(user_id: str) -> None:
#     db = MySQLdb.connect(DB_URL, DB_CARD, DB_PASS, DB_LIB, charset='utf8')
#     cursor = db.cursor()
#     sql = "insert into user_info_new(user_id,user_coin,user_health,user_crime,user_coin_max) values (%s,100,100,0,100)"
#     args = (user_id,)
#     cursor.execute(sql, args)
#     db.commit()
#     db.close()


# # 扣费
# # 减少user_id的user_coin字段
# def reduce_user_coin(user_id: str, user_coin: int) -> None:
#     db = MySQLdb.connect(DB_URL, DB_CARD, DB_PASS, DB_LIB, charset='utf8')
#     cursor = db.cursor()
#     sql = f"update user_info_new set user_coin=user_coin-{user_coin} where user_id='{user_id}'"
#     cursor.execute(sql)
#     db.commit()
#     db.close()


# # 修改画境币
# def change_user_crime(user_id: str, num: str) -> None:
#     db = MySQLdb.connect(DB_URL, DB_CARD, DB_PASS, DB_LIB, charset='utf8')
#     cursor = db.cursor()
#     sql = f"update user_info_new set user_crime=user_crime{num} where user_id='{user_id}'"
#     cursor.execute(sql)
#     db.commit()
#     db.close()


# # 修改行动点上限
# def change_coin_max(user_id: str, num: int) -> None:
#     db = MySQLdb.connect(DB_URL, DB_CARD, DB_PASS, DB_LIB, charset='utf8')
#     cursor = db.cursor()
#     sql = f"update user_info_new set user_coin_max={num} where user_id='{user_id}'"
#     cursor.execute(sql)
#     db.commit()
#     db.close()





def get_user_info_new(user_id: str) -> Optional[Tuple]:
    """查询user_info_new表"""
    sql = "SELECT * FROM user_info_new WHERE user_id=%s"
    return db.sql_dql(sql, (user_id,))

def get_user_info_old(user_id: str) -> Optional[Tuple]:
    """查询user_info表"""
    sql = "SELECT * FROM user_info WHERE user_id=%s"
    return db.sql_dql(sql, (user_id,))

def insert_user_info_new(user_id: str) -> bool:
    """向user_info_new表中插入数据"""
    sql = """INSERT INTO user_info_new
             (user_id, user_coin, user_health, user_crime, user_coin_max)
             VALUES (%s, 100, 100, 0, 100)"""
    return db.sql_dml(sql, (user_id,)) > 0

def reduce_user_coin(user_id: str, user_coin: int) -> bool:
    """减少用户金币"""
    sql = "UPDATE user_info_new SET user_coin=user_coin-%s WHERE user_id=%s"
    return db.sql_dml(sql, (user_coin, user_id)) > 0

def change_user_crime(user_id: str, num: str) -> bool:
    """修改画境币"""
    # 注意：这里num应该包含操作符，如"+1"或"-1"
    sql = f"UPDATE user_info_new SET user_crime=user_crime{num} WHERE user_id=%s"
    return db.sql_dml(sql, (user_id,)) > 0

def change_coin_max(user_id: str, num: int) -> bool:
    """修改行动点上限"""
    sql = "UPDATE user_info_new SET user_coin_max=%s WHERE user_id=%s"
    return db.sql_dml(sql, (num, user_id)) > 0