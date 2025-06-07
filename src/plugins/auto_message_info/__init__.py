'''
Author: 七画一只妖
Date: 2022-01-23 13:17:33
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-05-31 23:40:40
Description: file content
'''
from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent


from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name='静默者-消息记录',
    description='功能：记录机器人所在群每条发言记录',
    usage='''使用方式：无【静默模块】''',
    extra={'version': 'v0.0.1',
           'cost': '无消耗'}
)


# 注册消息响应器
message_handle = on_message(block=False, priority=1)


# 记录每条发言
@message_handle.handle()
async def _(event: MessageEvent, e: GroupMessageEvent):
    print("消息！")