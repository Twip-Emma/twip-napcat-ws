import asyncio
import base64
import aiofiles
from pathlib import Path
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

ABSOLUTE_PATH = Path(__file__).absolute().parents[0]
TEXT_FILE = ABSOLUTE_PATH / "测试.txt"

upload_test = on_command(
    "-导出测试",
    priority=10,
    block=True
)

@upload_test.handle()
async def handle_export(bot: Bot, event: GroupMessageEvent):
    try:
        # 读取文件并 base64 编码
        async with aiofiles.open(TEXT_FILE, "rb") as f:
            file_content = await f.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # 尝试使用 base64 格式上传
        result = await bot.call_api(
            "upload_group_file",
            group_id=event.group_id,
            file=f"base64://{file_base64}",  # base64 格式
            name="测试.txt"
        )
        
        await upload_test.finish("文件上传成功！")
        
    except Exception as e:
        await upload_test.finish(f"文件上传失败: {str(e)}")