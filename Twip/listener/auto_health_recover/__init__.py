'''
Author: 七画一只妖
Date: 2022-06-21 14:44:44
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-06-07 11:28:08
Description: file content
'''

import datetime

import pytz
from nonebot import require
from nonebot.plugin import PluginMetadata
from tool.utils import db

__plugin_meta__ = PluginMetadata(
    name='静默者-健康回复',
    description='功能：涩图功能的健康回复系统',
    usage='''使用方式：无【静默模块】''',
    extra={'version': 'v0.0.1',
           'cost': '无消耗'}
)


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", hour="*")
async def _():
    now = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
    if now.hour % 3 == 0:
        sql = "update user_info_new set user_health=user_health+1 where user_health<100"
        db.sql_dml(sql)


@scheduler.scheduled_job("cron", hour="*")
async def _():
    sql = "update user_info_new set user_coin=IF(user_coin + 10 > user_coin_max, user_coin, user_coin + 10)"
    db.sql_dml(sql)