'''
Author: 七画一只妖
Date: 2022-01-23 12:47:41
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-06-07 12:12:24
Description: file content
'''
import os
import json


from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from functools import wraps

from .user_database import get_user_info_new, insert_user_info_new, reduce_user_coin


_PATH = os.path.dirname(__file__)
_FILE_PATH = os.path.join(_PATH, "data", "power.json")


def _get_data():
    data:dict = json.load(open(_FILE_PATH, 'r', encoding='utf8'))
    level_S:list = data["level_S"]
    level_A:list = data["level_A"]
    ban_user:list = data["ban_user"]
    return level_S, level_A, ban_user


# 权限校验：S
def is_level_S(func):
    @wraps(func)
    async def check_power(*args, **kwargs):
        level_S, _, ban_user = _get_data()
        cost = None
        group_id = None
        for k, v in kwargs.items():
            if k == 'event':
                user_id = str(v.user_id)
                try:
                    group_id = str(v.group_id)
                except:
                    group_id = "x"
                if user_id in ban_user:
                    return
                if group_id not in level_S:
                    return
            if k == "cost":
                cost = v
        if not delete_user_coin(user_id=user_id, cost=cost):
            return
        return await func(*args, **kwargs)
    return check_power


# 手动校验
def is_level_is_inner(event: GroupMessageEvent) -> bool:
    level_S, _, ban_user = _get_data()
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    print(f"无权限的用户 群号:{group_id}, qq号:{user_id}")
    if user_id in ban_user:
        return False
    if group_id not in level_S:
        return False
    return True


# 权限校验：A
def is_level_A(func):
    @wraps(func)
    async def check_power(*args, **kwargs):
        _, level_A, ban_user = _get_data()
        cost = None
        for k, v in kwargs.items():
            if k == 'event':
                user_id = str(v.user_id)
                try:
                    group_id = str(v.group_id)
                except:
                    group_id = "x"
                if user_id in ban_user:
                    return
                if group_id not in level_A:
                    return
            if k == "cost":
                cost = v
        if not delete_user_coin(user_id=user_id, cost=cost):
            return
        return await func(*args, **kwargs)
    return check_power


# 行动点扣除
def delete_user_coin(user_id:str, cost:int) -> bool:
    user_data = get_user_info_new(user_id=user_id)
    print(user_data)
    if not user_data:
        insert_user_info_new(user_id=user_id)
        user_data = get_user_info_new(user_id=user_id)
    if user_data[0][1] >= cost:
        reduce_user_coin(user_id=user_id, user_coin=cost)
        return True
    else:
        return False
