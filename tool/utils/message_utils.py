import re

def parse_message(message):
    # 正则表达式匹配图片内容
    image_pattern = re.compile(r'\[CQ:image.*?url=(.*?)(?:,|\])')
    
    # 查找所有图片的url
    urls = image_pattern.findall(message)
    
    # 处理url，将&amp;替换为&
    processed_urls = [url.replace('&amp;', '&') for url in urls]
    
    # 拼接多个url，用分号分隔
    url = ';'.join(processed_urls) if processed_urls else None
    
    # 替换图片部分为【图片】
    context = re.sub(r'\[CQ:image.*?\]', '【图片】', message)
    
    # 如果context与原始message相同，说明没有图片
    if context == message:
        context = message if message else None
    else:
        # 如果替换后context为空或只有【图片】，则context为None
        if not context.strip() or re.fullmatch(r'^(【图片】)+$', context.strip()):
            context = None
    
    return {
        'context': context,
        'url': url if url else None
    }