import time
import base64
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata

from tool.find_power.format_data import is_level_S
from tool.utils.logger import logger as my_logger

from .payload import get_data


__plugin_meta__ = PluginMetadata(
    name='棕色尘埃2兑换码',
    description='自动兑换兑换码',
    usage='''使用方式(参数之间有空格)：\n绑定<游戏昵称>\n删除绑定\n兑换<兑换码>''',
    extra={'version': 'v2.0.0',
           'cost': '15'}
)


user_bind = on_command("绑定", block=True, priority=2)
@user_bind.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=15):
    user_id = str(event.user_id)
    args = str(event.get_message()).strip().split()
    if len(args) != 2:
        await user_bind.finish("格式错误，请用：绑定+(空格)+(游戏昵称)")
    command, nickname = args
    success, msg = await get_data.user_bind(user_id=user_id, nickname=nickname)
    await user_bind.finish(msg)


user_delete = on_command("删除绑定", block=True, priority=2)
@user_delete.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=15):
    user_id = str(event.user_id)
    success, msg = await get_data.delete_user_bindings(user_id=user_id)
    await user_bind.finish(msg)


user_redeem = on_command("兑换", block=True, priority=2)
@user_redeem.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=50):
    user_id = str(event.user_id)
    args = str(event.get_message()).strip().split()
    if len(args) != 2:
        await user_bind.finish("格式错误，请用：兑换+(空格)+(兑换码)")
    command, coupon_code = args
    msg = await get_data.redeem_coupon(user_id=user_id, coupon_code=coupon_code)
    await user_bind.finish(msg)


user_redeem = on_command("兑换全部", block=True, priority=2)
@user_redeem.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=5):
    user_id = str(event.user_id)
    await user_bind.finish(f"qq={user_id}，本功能维护中")
