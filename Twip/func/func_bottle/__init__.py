import time
import base64
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.permission import SUPERUSER
import random

from tool.find_power.format_data import is_level_S
from tool.utils.logger import logger as my_logger
from tool.QsPilUtils2.dao import text_to_image

from .payload import db_service, bottle_service


__plugin_meta__ = PluginMetadata(
    name='漂流瓶',
    description='你trytry就晓得了',
    usage='''
    <ft color=(255,0,0)>30</ft>丢瓶子
    <ft color=(255,0,0)>20</ft>捡瓶子
    '''
)


add_bottle = on_command(cmd = "X丢瓶子", block=True, priority=2)
@add_bottle.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=20):
    user_id = str(event.user_id)
    args = str(event.get_message()).strip().split()
    if len(args) == 1:
        await add_bottle.finish("格式错误，请发送以下命令查看标准格式：\n菜单 漂流瓶")
    command, *content = args
    if len(content) > 5000:
        await add_bottle.finish("你发这么长想干嘛？")
    success = db_service.add_bottle(user_id = user_id, content = ''.join(map(str, content)))
    if success:
        await add_bottle.finish(command + "成功")
        # ran:int = random.randint(1,100)
        # if (ran < 20):
        #     msg = bottle_service.get_treasure_by_add(user_id = user_id)
        #     await select_bottle.finish(msg)
    else:
        await add_bottle.finish("添加失败，请联系管理员（拿上时间截图招管理员拿币）")


select_bottle = on_command(cmd = "X捡瓶子", block=True, priority=2)
@select_bottle.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=20):
    user_id = str(event.user_id)
    command = str(event.get_message()).strip().split()
    if len(command) == 1:
        # 概率获得捡到宝箱
        ran:int = random.randint(1,100)
        if (ran < 40):
            msg = await bottle_service.get_treasure_by_select(user_id = user_id)
            await select_bottle.send(msg)
        else:
            data = db_service.select_bottle()
            if data:
                image_path = text_to_image(data[1], 15, (10, 10))
                with open(image_path, "rb") as f:
                    image_data = f.read()
                base64_str = f"base64://{base64.b64encode(image_data).decode()}"
                image_msg = MessageSegment.image(base64_str)
                await select_bottle.finish(image_msg)
            else:
                await select_bottle.finish(command[0] + "失败，请联系管理员（拿上时间截图招管理员拿币）")
    else:
        await select_bottle.finish("格式错误，请发送以下命令查看标准格式：\n菜单 漂流瓶")


















