'''
Author: tanyongqiang 1157529280@qq.com
Date: 2025-05-31 23:26:35
LastEditors: tanyongqiang 1157529280@qq.com
LastEditTime: 2025-06-03 09:31:12
FilePath: \twip-napcat\bot.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import nonebot
from nonebot import require
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter
# from nonebot.log import logger, logger_id
# logger.remove(logger_id)
import os
from pathlib import Path
import logging
from datetime import datetime

from os import path
import sys

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)



from os import path
import sys

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

# 定时任务
nonebot.init(apscheduler_autostart=True)
nonebot.init(apscheduler_config={
    "apscheduler.timezone": "Asia/Shanghai"
})

# 测试模块
# nonebot.load_plugins("src/plugins")

# 正式模块
# nonebot.load_plugins("src/plugins/admin")
# nonebot.load_plugins("Twip/func")
# nonebot.load_plugins("src/plugins/user")
# nonebot.load_plugins("src/plugins/listener")
# nonebot.load_plugins("src/plugins/speaker")
# nonebot.load_plugins("src/plugins/help")

# 单模块
nonebot.load_plugin("Twip")

# 全局模块
# nonebot.load_plugin()

# 加载插件市场的
# require("nonebot_plugin_memes")
# nonebot.load_plugin("nonebot_plugin_memes")

# 加载绝对路径头
ABSOLUTE_PATH = path.join(path.dirname(__file__))


def setup_logging():
    # 获取当前文件所在目录
    base_dir = Path(__file__).parent
    
    # 创建log目录（如果不存在）
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 按日期设置日志文件名
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"{log_date}.log"
    
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),  # 写入文件
            logging.StreamHandler()         # 同时输出到控制台
        ]
    )


if __name__ == "__main__":
     # 设置日志
    setup_logging()
    
    # 获取绝对路径并添加工具目录到系统路径
    ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
    tool_path = os.path.join(ABSOLUTE_PATH, "tool")
    sys.path.append(tool_path)
    
    # 启动nonebot
    logging.info("Starting NoneBot...")
    try:
        nonebot.run()
    except Exception as e:
        logging.error(f"NoneBot failed to start: {str(e)}")
        raise




