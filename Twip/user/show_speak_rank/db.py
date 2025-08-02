'''
Author: 七画一只妖
Date: 2022-03-01 20:27:54
LastEditors: 七画一只妖 1157529280@qq.com
LastEditTime: 2023-09-22 19:53:28
Description: file content
'''

import base64
import datetime
from io import BytesIO
import time
from tool.utils import db
import MySQLdb
from pathlib import Path
from Twip import TTF_PATH

from PIL import Image, ImageDraw, ImageFont

FILE_PATH = Path(__file__).parent.absolute()
    
# 构建字体文件路径（自动处理路径分隔符）
FONT_PATH = FILE_PATH / "consola-1.ttf"


# 设定一个时间 2021年1月20日
# WS机器人统计时间 2025年7月25日
OLD_TIME = time.strptime("2025-07-25 00:00:00", "%Y-%m-%d %H:%M:%S")


# 获取现在的时间
def get_now_time() -> str:
    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return now_time


def find_speak_rank() -> list:
    sql = "select * from user_info order by speak_time_total desc limit 0,99;"
    results = db.sql_dql(sql, ())
    return results


# 将数据转成图片返回image对象
def data_to_image(data,type:str) -> str:
    # 获取当前时间
    now_time = get_now_time()
    # 获取时间差
    time_difference = time.mktime(time.strptime(now_time, "%Y-%m-%d %H:%M:%S")) - time.mktime(OLD_TIME)
    # 将时间差转换
    day =int( time_difference // (24 * 60 * 60))
    hour = int((time_difference - day * 24 * 60 * 60) // (60 * 60))
    minute = int((time_difference - day * 24 * 60 * 60 - hour * 60 * 60) // 60)
    second = int(time_difference - day * 24 * 60 * 60 - hour * 60 * 60 - minute * 60)
    time_difference = f"{day} 天 {hour} 小时 {minute} 分 {second} 秒"



    ################################################
    text1 = ""
    rank = 1
    for item in data:
        # user_item = f"【{str(rank)}】{item[0]}({item[1]})的发言次数是：{item[4]}\n\n"
        # 对齐
        user_item = f"[{str(rank):>2}] ===> {item[4]:>6}   |\n\n"
        text1 += user_item
        rank += 1
    bg = Image.new("RGB",(650,5000), (255,255,255))
    dr = ImageDraw.Draw(bg)
    font = ImageFont.truetype(FONT_PATH, 20)
    dr.text((10,200), text=text1, font=font, fill="#000000")
    ################################################
    text2 = ""
    rank = 1
    for item in data:
        # user_item = f"【{str(rank)}】{item[0]}({item[1]})的发言次数是：{item[4]}\n\n"
        # 对齐
        # item[1]是一个字符串，将这个字符串的开头两个字符和结尾两个字符换成*号
        if type == "admin":
            user_item = f"{item[0]} ( {item[1]} ) \n\n"
        else:
            user_item = f"{item[0]} ( {item[1][:4]}{'*'*(len(item[1])-4)} ) \n\n"
        # user_item = f"{item[0]} ( {item[1]} ) \n\n"
        text2 += user_item
        rank += 1
    dr = ImageDraw.Draw(bg)
    font = ImageFont.truetype(TTF_PATH, 19)
    dr.text((275,200), text=text2, font=font, fill="#000000")
    ################################################
    text3 = f"当前时间：{now_time}\n\n"
    text4 = f"统计时长：{time_difference}\n\n"
    dr = ImageDraw.Draw(bg)
    font = ImageFont.truetype(TTF_PATH, 19)

    # 使用getbbox()获取文本尺寸（新版Pillow）
    bbox3 = font.getbbox(text3)  # 返回(left, top, right, bottom)
    text_width3 = (bbox3[2] - bbox3[0], bbox3[3] - bbox3[1])  # (width, height)

    bbox4 = font.getbbox(text4)
    text_width4 = (bbox4[2] - bbox4[0], bbox4[3] - bbox4[1])

    bbox5 = font.getbbox("By  Twip  七画一只妖")
    text_width5 = (bbox5[2] - bbox5[0], bbox5[3] - bbox5[1])

    # 绘制文本（保持原有布局逻辑）
    dr.text(((650 - text_width3[0]) / 2, 20), text=text3, font=font, fill="#000000")
    dr.text(((650 - text_width4[0]) / 2, 20 + text_width3[1]), text=text4, font=font, fill="#000000")
    dr.text(((650 - text_width5[0]) / 2, 20 + text_width3[1] + text_width4[1]), 
        text="By  Twip  七画一只妖", font=font, fill="#000000")

    # 大字号标题
    font_large = ImageFont.truetype(TTF_PATH, 40)
    bbox6 = font_large.getbbox("发 言 总 排 行 榜")
    text_width6 = (bbox6[2] - bbox6[0], bbox6[3] - bbox6[1])

    dr.text(((650 - text_width6[0]) / 2, 40 + text_width3[1] + text_width4[1] + text_width5[1]), 
        text="发 言 总 排 行 榜", font=font_large, fill="#000000")

    return img_to_b64(bg)


# 获取当日发言排名
def get_speak_rank_today(type:str):
    now_time = datetime.datetime.now().strftime('%Y-%m-%d')
    sql = "select * from t_bot_listener_speaklog where speak_time=%s order by speak_count desc limit 0,99;"
    data = db.sql_dql(sql, (now_time,))

    ################################################
    text1 = ""
    rank = 1
    for item in data:
        # user_item = f"【{str(rank)}】{item[0]}({item[1]})的发言次数是：{item[4]}\n\n"
        # 对齐
        user_item = f"[{str(rank):>2}] ===> {item[4]:>6}   |\n\n"
        text1 += user_item
        rank += 1
    bg = Image.new("RGB",(650,5000), (255,255,255))
    dr = ImageDraw.Draw(bg)
    font = ImageFont.truetype(FONT_PATH, 20)
    dr.text((10,200), text=text1, font=font, fill="#000000")
    ################################################
    text2 = ""
    rank = 1
    for item in data:
        # user_item = f"【{str(rank)}】{item[0]}({item[1]})的发言次数是：{item[4]}\n\n"
        # 对齐
        # item[1]是一个字符串，将这个字符串的开头两个字符和结尾两个字符换成*号
        if type == "admin":
            user_item = f"{item[2]} ( {item[1]} ) \n\n"
        else:
            user_item = f"{item[2]} ( {item[1][:4]}{'*'*(len(item[1])-4)} ) \n\n"
        # user_item = f"{item[0]} ( {item[1]} ) \n\n"
        text2 += user_item
        rank += 1
    dr = ImageDraw.Draw(bg)
    font = ImageFont.truetype(TTF_PATH, 19)
    dr.text((275,200), text=text2, font=font, fill="#000000")
    ################################################
    text3 = f"当前时间：{now_time}\n\n"
    text4 = f"统计时长：今天0点到目前为止\n\n"
    dr = ImageDraw.Draw(bg)
    font = ImageFont.truetype(TTF_PATH, 19)

    # 使用getbbox()获取文本尺寸（新版方法）
    bbox3 = font.getbbox(text3)  # 返回(left, top, right, bottom)
    text_width3 = bbox3[2] - bbox3[0]  # 宽度 = right - left
    text_height3 = bbox3[3] - bbox3[1]  # 高度 = bottom - top

    bbox4 = font.getbbox(text4)
    text_width4 = bbox4[2] - bbox4[0]
    text_height4 = bbox4[3] - bbox4[1]

    bbox5 = font.getbbox("By  Twip  七画一只妖")
    text_width5 = bbox5[2] - bbox5[0]
    text_height5 = bbox5[3] - bbox5[1]

    # 绘制文本（保持原有布局）
    dr.text(((650 - text_width3) / 2, 20), text=text3, font=font, fill="#000000")
    dr.text(((650 - text_width4) / 2, 20 + text_height3), text=text4, font=font, fill="#000000")
    dr.text(((650 - text_width5) / 2, 20 + text_height3 + text_height4), 
        text="By  Twip  七画一只妖", font=font, fill="#000000")

    # 大字号标题
    font_large = ImageFont.truetype(TTF_PATH, 40)
    bbox6 = font_large.getbbox("当 日 发 言 排 行 榜")
    text_width6 = bbox6[2] - bbox6[0]
    text_height6 = bbox6[3] - bbox6[1]

    dr.text(((650 - text_width6) / 2, 40 + text_height3 + text_height4 + text_height5), 
        text="当 日 发 言 排 行 榜", font=font_large, fill="#000000")

    return img_to_b64(bg)
    


def img_to_b64(pic: Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getbuffer()).decode()
    return "base64://" + base64_str