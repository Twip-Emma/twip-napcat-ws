import time
import base64
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER

from tool.find_power.format_data import is_level_S
from tool.utils.logger import logger as my_logger
from tool.QsPilUtils2.dao import text_to_image

from .payload import get_data


__plugin_meta__ = PluginMetadata(
    name='兑换码',
    description='棕色尘埃2自动兑换兑换码',
    usage='''使用方式(参数之间有空格)：\n绑定<游戏昵称>\n删除绑定\n兑换<兑换码>\n兑换全部\n兑换码列表（超级管理员）\n添加兑换码<兑换码><描述><yyyy-MM-dd/永久>（超级管理员）\n删除兑换码<兑换码>（超级管理员）''',
    extra={'version': 'v2.0.0',
           'cost': '15'}
)


user_bind = on_command("绑定", block=True, priority=2)
@user_bind.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=10):
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
async def _(bot: Bot, event: GroupMessageEvent, cost=10):
    user_id = str(event.user_id)
    success, msg = await get_data.delete_user_bindings(user_id=user_id)
    await user_bind.finish(msg)


user_redeem = on_command("兑换", block=True, priority=2)
@user_redeem.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=30):
    user_id = str(event.user_id)
    args = str(event.get_message()).strip().split()
    if len(args) != 2:
        await user_bind.finish("格式错误，请用：兑换+(空格)+(兑换码)")
    command, coupon_code = args
    msg = await get_data.redeem_coupon(user_id=user_id, coupon_code=coupon_code)
    await user_bind.finish(msg)


user_redeem_all = on_command("兑换全部", block=True, priority=2)
@user_redeem_all.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=80):
    user_id = str(event.user_id)
    await user_bind.send(f"user_id={user_id}:开始处理，耗时较久请耐心等待")
    result = await get_data.redeem_all_coupons_for_user(user_id)
    image_path = text_to_image(result, 10, (10, 10))
    with open(image_path, "rb") as f:
        image_data = f.read()
    base64_str = f"base64://{base64.b64encode(image_data).decode()}"
    image_msg = MessageSegment.image(base64_str)
    await user_bind.finish(image_msg)


get_coupon_all = on_command("兑换码列表", block=True, permission=SUPERUSER, priority=2)
@get_coupon_all.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=0):
    result = await get_data.get_coupon_all()
    image_path = text_to_image(result)
    with open(image_path, "rb") as f:
        image_data = f.read()
    base64_str = f"base64://{base64.b64encode(image_data).decode()}"
    image_msg = MessageSegment.image(base64_str)
    await user_bind.finish(image_msg)


add_coupon = on_command("添加兑换码", block=True, permission=SUPERUSER, priority=2)
@add_coupon.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=0):
    args = str(event.get_message()).strip().split()
    if len(args) != 4:
        await add_coupon.finish("格式错误，请用：添加兑换码<兑换码><描述><yyyy-MM-dd/永久>")
    result = await get_data.add_coupon(args[1], args[2], args[3])
    await add_coupon.finish(result)


delete_coupon = on_command("删除兑换码", block=True, permission=SUPERUSER, priority=2)
@delete_coupon.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=0):
    args = str(event.get_message()).strip().split()
    if len(args) != 4:
        await delete_coupon.finish("格式错误，请用：删除兑换码<兑换码>")
    result = await get_data.delete_coupon(args[1])
    await delete_coupon.finish(result)
















