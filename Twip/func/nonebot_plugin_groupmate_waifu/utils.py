import io
import httpx
import hashlib
import asyncio
import json

from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple
import html
import re
from Twip import TTF_PATH

async def download_avatar(user_id: int) -> bytes:
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        data = await download_url(url)
    return data

async def download_url(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        for i in range(3):
            try:
                resp = await client.get(url, timeout=20)
                resp.raise_for_status()
                return resp.content
            except Exception:
                await asyncio.sleep(3)
    raise Exception(f"{url} 下载失败！")

async def download_user_img(user_id: int) -> bytes:
    data = await download_avatar(user_id)
    img = Image.open(io.BytesIO(data))
    
    # 转换为PNG格式并返回bytes
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()

async def user_img(user_id: int) -> str:
    '''
    获取用户头像url
    '''
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = await download_url(url)
    if hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
    return url

class TextRenderer:
    def __init__(self, font_size: int = 50, spacing: int = 10):
        self.font_size = font_size
        self.spacing = spacing
        try:
            # 尝试加载系统字体
            self.font = ImageFont.truetype(TTF_PATH, font_size)
        except:
            try:
                # 备用字体
                self.font = ImageFont.truetype(TTF_PATH, font_size)
            except:
                # 使用默认字体
                self.font = ImageFont.load_default()
    
    def get_text_size(self, text: str) -> Tuple[int, int]:
        """获取文本尺寸"""
        bbox = self.font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    def get_multiline_text_size(self, text: str) -> Tuple[int, int]:
        """获取多行文本尺寸"""
        lines = text.split('\n')
        max_width = 0
        total_height = 0
        
        for i, line in enumerate(lines):
            width, height = self.get_text_size(line)
            max_width = max(max_width, width)
            total_height += height
            if i < len(lines) - 1:
                total_height += self.spacing
        
        return max_width, total_height

def text_to_png(msg: str, font_size: int = 50, spacing: int = 10) -> io.BytesIO:
    '''
    文字转png
    '''
    renderer = TextRenderer(font_size, spacing)
    
    # 计算文本尺寸
    width, height = renderer.get_multiline_text_size(msg)
    
    # 创建图像，添加边距
    padding = 20
    img_width = width + padding * 2
    img_height = height + padding * 2
    
    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)
    
    # 绘制文本
    lines = msg.split('\n')
    y = padding
    for line in lines:
        if line.strip():  # 非空行
            draw.text((padding, y), line, fill="black", font=renderer.font)
        # 移动到下一行
        line_height = renderer.get_text_size(line)[1] if line.strip() else renderer.font_size
        y += line_height + spacing
    
    # 保存到BytesIO
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output

def bbcode_to_png(msg: str, spacing: int = 10) -> io.BytesIO:
    '''
    bbcode文字转png - 简化版，移除BBCode标签后渲染
    '''
    # 简单的BBCode标签移除
    def remove_bbcode(text: str) -> str:
        # 移除常见的BBCode标签
        patterns = [
            r'\[b\](.*?)\[/b\]',  # 粗体
            r'\[i\](.*?)\[/i\]',  # 斜体
            r'\[u\](.*?)\[/u\]',  # 下划线
            r'\[color=.*?\](.*?)\[/color\]',  # 颜色
            r'\[size=.*?\](.*?)\[/size\]',  # 大小
            r'\[url.*?\](.*?)\[/url\]',  # 链接
            r'\[img\](.*?)\[/img\]',  # 图片
        ]
        
        result = text
        for pattern in patterns:
            result = re.sub(pattern, r'\1', result)
        
        # 移除所有其他BBCode标签
        result = re.sub(r'\[/?.*?\]', '', result)
        
        return html.unescape(result)  # 处理HTML实体
    
    # 移除BBCode标签后使用普通文本渲染
    clean_text = remove_bbcode(msg)
    return text_to_png(clean_text, 50, spacing)

def get_message_at(data: str) -> List[int]:
    '''
    获取at列表
    :param data: event.json()
    '''
    qq_list = []
    try:
        data_dict = json.loads(data)
        for msg in data_dict.get('message', []):
            if msg.get('type') == 'at':
                qq_list.append(int(msg['data']['qq']))
    except (json.JSONDecodeError, KeyError, ValueError):
        pass
    
    return qq_list