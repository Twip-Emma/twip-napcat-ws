'''
Author: 七画一只妖 1157529280@qq.com
Date: 2023-08-10 09:18:08
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-05-31 23:33:05
'''
import asyncio
import random
import re
from pathlib import Path

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata


BASE_PATH: str = Path(__file__).absolute().parents[0]
pattern = re.compile(r"url=(.*?)&amp;")


rank = on_command("测试", aliases={"测试"}, block=True, priority=1)


@rank.handle()
async def _(bot: Bot, event: GroupMessageEvent, cost=0):
    print("123")
    await rank.send("111")
    