import base64
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from tool.find_power.format_data import is_level_S
from tool.utils.logger import logger as my_logger
from tool.QsPilUtils2.dao import text_to_image
from tool.find_power.user_database import get_user_info_new, insert_user_info_new, change_user_crime, change_coin_max


__plugin_meta__ = PluginMetadata(
    name='???',
    description='???',
    usage='''???\n???''',
    extra={'version': 'v1.0.0',
           'cost': '无消耗'}
)


test_1 = on_command(":*", block=True, priority=2)


# 个人信息
@test_1.handle()
@is_level_S
async def _(bot: Bot, event: GroupMessageEvent, cost=0):
    group_id = str(event.group_id)
    user_id = str(event.user_id)

    recall_user_info = await bot.get_group_member_list(group_id=group_id)
    print("【测试1】开始")
    print(recall_user_info)

    

    
    # await test_1.send(image_msg)
