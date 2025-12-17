import jieba
import re
import json
from datetime import datetime
from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from nonebot.plugin import PluginMetadata
from typing import List, Dict, Any
from tool.find_power.format_data import is_level_S
from tool.utils.logger import logger as my_logger
from tool.utils import db
from pathlib import Path
BASE_PATH: str = Path(__file__).absolute().parents[0]


__plugin_meta__ = PluginMetadata(
    name='我的热词',
    description='查看自己或者当前群的热词排行',
    usage='''
    使用方式(参数之间有空格)：
    =========================
    热词<@某人(可选)>
    群热词
    <ft color=(255,0,0)>超级管理员</ft>重置热词统计
    <ft color=(255,0,0)>超级管理员</ft>同步老数据
    ''',
    extra={'version': 'v2.0.0',
           'cost': '15'}
)


# 统计所有分词
STATISTIC_ALL = True  # 是否统计所有分词
MIN_WORD_LENGTH = 2   # 最小词长
MAX_WORD_LENGTH = 10  # 最大词长

# 过滤词列表（不统计的词）
STOP_WORDS = {
"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到",
"说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这"
}

# 创建消息处理器
message_handle = on_message(block=False, priority=1)

def extract_keywords(message: str) -> List[str]:
    """
    从消息中提取关键词
    """
    # 移除特殊字符和空格
    message = re.sub(r'[^\w\u4e00-\u9fff]+', ' ', message)
    
    keywords = []
    
    # 使用jieba分词
    words = jieba.cut(message, cut_all=False)
    for word in words:
        # 过滤条件
        if (MIN_WORD_LENGTH <= len(word) <= MAX_WORD_LENGTH and 
            word not in STOP_WORDS and 
            not word.isdigit() and 
            not re.match(r'^[a-zA-Z]+$', word)):
            keywords.append(word)
    
    return list(set(keywords))  # 去重

def check_and_update_record(user_id: str, group_id: str, keyword: str) -> None:
    """
    检查并更新数据库记录
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 检查是否已存在该用户在该群组的该关键词记录
    check_sql = """
    SELECT id, count FROM message_analyze 
    WHERE user_id = %s AND group_id = %s AND key_word = %s AND is_deleted = FALSE
    """
    result = db.sql_dql(check_sql, (user_id, group_id, keyword))
    
    if result and len(result) > 0:
        # 更新现有记录
        record = result[0]
        record_id = record[0]
        current_count = record[1]
        
        update_sql = """
        UPDATE message_analyze 
        SET count = %s, update_time = %s 
        WHERE id = %s
        """
        db.sql_dml(update_sql, (current_count + 1, current_time, record_id))
    else:
        # 创建新记录
        insert_sql = """
        INSERT INTO message_analyze 
        (user_id, group_id, key_word, count, create_time, update_time, is_deleted, is_sensitive)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.sql_dml(insert_sql, (
            user_id, group_id, keyword, 1, 
            current_time, current_time, False, False
        ))

@message_handle.handle()
async def _(event: MessageEvent, e: GroupMessageEvent):
    try:
        message = str(event.get_message())
    except:
        message = "消息错误，可能是太长了，这是个xml卡片或者分享链接"
    
    # 过滤掉图片、表情等非文本消息
    if any(mark in message for mark in ["[CQ:image", "[CQ:face", "[CQ:record", "[CQ:video"]):
        return
    
    user_id = str(e.user_id)
    group_id = str(e.group_id)

    # 长度大于50的不纳入统计
    if len(message) > 50:
        return
    
    # 提取关键词
    keywords = extract_keywords(message)
    
    if not keywords:
        return
    
    # 更新每个关键词的统计
    for keyword in keywords:
        # 确保关键词长度不超过数据库字段限制
        if len(keyword) > 10:
            keyword = keyword[:10]
        
        try:
            check_and_update_record(user_id, group_id, keyword)
        except Exception as db_error:
            # 记录错误但不中断程序
            print(f"数据库操作失败: {db_error}")
            continue

# 查询统计数据的函数
def get_user_keyword_stats(user_id: str, group_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取用户在该群组的关键词统计
    """
    sql = """
    SELECT key_word, count 
    FROM message_analyze 
    WHERE user_id = %s AND group_id = %s AND is_deleted = FALSE
    ORDER BY count DESC 
    LIMIT %s
    """
    
    result = db.sql_dql(sql, (user_id, group_id, limit))
    
    stats = []
    for row in result:
        stats.append({
            "keyword": row[0],
            "count": row[1]
        })
    
    return stats

def get_group_keyword_stats(group_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取群组的关键词统计
    """
    sql = """
    SELECT key_word, SUM(count) as total_count
    FROM message_analyze 
    WHERE group_id = %s AND is_deleted = FALSE
    GROUP BY key_word
    ORDER BY total_count DESC
    LIMIT %s
    """
    
    result = db.sql_dql(sql, (group_id, limit))
    
    stats = []
    for row in result:
        stats.append({
            "keyword": row[0],
            "total_count": row[1]
        })
    
    return stats

def get_user_total_stats(user_id: str, group_id: str) -> Dict[str, Any]:
    """
    获取用户在该群组的总体统计
    """
    # 总关键词数
    total_sql = """
    SELECT SUM(count) 
    FROM message_analyze 
    WHERE user_id = %s AND group_id = %s AND is_deleted = FALSE
    """
    total_result = db.sql_dql(total_sql, (user_id, group_id))
    total_count = total_result[0][0] if total_result and total_result[0][0] else 0
    
    # 不同关键词数
    distinct_sql = """
    SELECT COUNT(DISTINCT key_word) 
    FROM message_analyze 
    WHERE user_id = %s AND group_id = %s AND is_deleted = FALSE
    """
    distinct_result = db.sql_dql(distinct_sql, (user_id, group_id))
    distinct_count = distinct_result[0][0] if distinct_result and distinct_result[0][0] else 0
    
    return {
        "total_keywords": total_count,
        "distinct_keywords": distinct_count,
        "user_id": user_id,
        "group_id": group_id
    }

# 添加一个命令来查询统计数据
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Message
from nonebot import on_command

stats_cmd = on_command("热词", aliases={"关键词", "keyword", "词频统计"}, priority=5)

@stats_cmd.handle()
@is_level_S
async def handle_stats(event: GroupMessageEvent, args: Message = CommandArg(), cost=0):
    user_id = str(event.user_id)
    group_id = str(event.group_id)
    
    arg_text = args.extract_plain_text().strip()
    
    try:
        if arg_text == "群组" or arg_text == "group" or arg_text == "本群":
            # 查询群组统计
            stats = get_group_keyword_stats(group_id, limit=10)
            if not stats:
                await stats_cmd.finish("本群暂无关键词统计数据")
            
            msg = "📊 群组关键词统计TOP10：\n"
            for i, stat in enumerate(stats, 1):
                msg += f"{i}. {stat['keyword']}: {stat['total_count']}次\n"
            
            await stats_cmd.finish(msg.strip())
        
        elif arg_text:
            # 查询指定用户（支持@用户）
            target_user = arg_text
            # 如果是@消息，提取用户ID
            if target_user.startswith("[CQ:at"):
                import re
                match = re.search(r'qq=(\d+)', target_user)
                if match:
                    target_user = match.group(1)
            
            stats = get_user_keyword_stats(target_user, group_id, limit=10)
            
            if not stats:
                await stats_cmd.finish(f"用户 {target_user} 暂无关键词统计数据")
            
            msg = f"📊 用户 {target_user} 关键词统计TOP10：\n"
            for i, stat in enumerate(stats, 1):
                msg += f"{i}. {stat['keyword']}: {stat['count']}次\n"
            
            await stats_cmd.finish(msg.strip())
        
        else:
            # 查询自己的统计
            stats = get_user_keyword_stats(user_id, group_id, limit=10)
            total_stats = get_user_total_stats(user_id, group_id)
            
            if not stats:
                await stats_cmd.finish("你还没有关键词统计数据")
            
            msg = f"📊 你的关键词统计TOP10：\n"
            msg += f"📈 总关键词次数: {total_stats['total_keywords']}\n"
            msg += f"🔤 不同关键词数: {total_stats['distinct_keywords']}\n\n"
            
            for i, stat in enumerate(stats, 1):
                msg += f"{i}. {stat['keyword']}: {stat['count']}次\n"
            
            await stats_cmd.finish(msg.strip())
            
    except Exception as e:
        my_logger.info('消息分析-关键词统计', f"查询失败: {str(e)}")

# 添加重置命令（仅管理员可用）
from nonebot.permission import SUPERUSER
reset_cmd = on_command("重置热词统计", permission=SUPERUSER, priority=5)

@reset_cmd.handle()
@is_level_S
async def handle_reset(event: GroupMessageEvent, args: Message = CommandArg(), cost=0):
    arg_text = args.extract_plain_text().strip()
    
    try:
        if arg_text == "本群":
            group_id = str(event.group_id)
            reset_sql = "DELETE FROM message_analyze WHERE group_id = %s"
            db.sql_dml(reset_sql, (group_id,))
            await reset_cmd.finish(f"已重置群组 {group_id} 的所有关键词统计")
        elif arg_text:
            # 重置指定用户
            reset_sql = "DELETE FROM message_analyze WHERE user_id = %s AND group_id = %s"
            group_id = str(event.group_id)
            db.sql_dml(reset_sql, (arg_text, group_id))
            await reset_cmd.finish(f"已重置用户 {arg_text} 在本群的关键词统计")
        else:
            await reset_cmd.finish("请指定重置范围：\n重置关键词统计 本群\n重置关键词统计 [用户ID]")
    except Exception as e:
        my_logger.info('消息分析-重置关键词统计', f"重置失败: {str(e)}")

# 添加热词排行榜命令
hot_cmd = on_command("群热词", aliases={"热词排行", "热词榜"}, priority=5)

@hot_cmd.handle()
@is_level_S
async def handle_hot(event: GroupMessageEvent, args: Message = CommandArg(), cost=0):
    group_id = str(event.group_id)
    
    try:
        # 查询最近7天的热词
        hot_sql = """
        SELECT key_word, SUM(count) as hot_count
        FROM message_analyze 
        WHERE group_id = %s 
          AND is_deleted = FALSE
          AND create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY key_word
        ORDER BY hot_count DESC
        LIMIT 10
        """
        
        result = db.sql_dql(hot_sql, (group_id,))
        
        if not result:
            await hot_cmd.finish("暂无最近7天的热词数据")
        
        msg = "🔥 最近7天热词排行榜：\n"
        for i, row in enumerate(result, 1):
            keyword = row[0]
            count = row[1]
            # 添加简单的热度标识
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            
            msg += f"{medal} {keyword}: {count}次\n"
        
        await hot_cmd.finish(msg.strip())
        
    except Exception as e:
        my_logger.info('消息分析-热词排行榜', f"查询热词失败: {str(e)}")

# 同步老数据
sync_cmd = on_command("同步老数据", permission=SUPERUSER, priority=5)

@sync_cmd.handle()
@is_level_S
async def handle_sync(event: GroupMessageEvent, args: Message = CommandArg(), cost=0):
    data:dict = json.load(open(Path(BASE_PATH) / "config.json", 'r', encoding='utf8'))
    id:int = data["oldMessageIdNow"]
    my_logger.info('消息分析-同步老数据', f"开始同步数据，当前指针位置：{id}")
    await sync_cmd.send(f"开始同步数据，当前已完成{str(id - 1)}条")
    
    try:
        while True:
            sql1 = "SELECT user_id, group_id, message_context FROM message_info WHERE id = %s"
            result = db.sql_dql(sql1, (id,))
            if result is ():
                await sync_cmd.finish(f"数据同步完成，当前指针位置：{id}")
                break
            message = result[0][2]

            # 长度大于50的不纳入统计
            if len(message) > 50 or "【纯图片】" in message:
                id += 1
                continue

            # 提取关键词
            keywords = extract_keywords(message)

            if not keywords:
                id += 1
                continue

            # 更新每个关键词的统计
            for keyword in keywords:
                # 确保关键词长度不超过数据库字段限制
                if len(keyword) > 10:
                    keyword = keyword[:10]
                check_and_update_record(result[0][0], result[0][1], keyword)
            # 持久化当前id
            id += 1
            data["oldMessageIdNow"] = id
            with open(Path(BASE_PATH) / "config.json", 'w', encoding='utf8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as db_error:
        data["oldMessageIdNow"] = id
        with open(Path(BASE_PATH) / "config.json", 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        my_logger.info(f"数据库操作失败: id={id}, error={db_error}")
        await sync_cmd.finish(f"数据同步异常，当前指针位置：{id}")


        

# 初始化jieba分词（可选：加载用户词典）
def init_jieba():
    """初始化jieba分词器"""
    # 可以加载自定义词典
    jieba.load_userdict(str(Path(BASE_PATH) / "词库-IK分词.txt"))
    jieba.load_userdict(str(Path(BASE_PATH) / "词库-jieba分词.txt"))
    jieba.load_userdict(str(Path(BASE_PATH) / "词库-mmseg分词.txt"))
    jieba.load_userdict(str(Path(BASE_PATH) / "词库-word分词.txt"))
    jieba.load_userdict(str(Path(BASE_PATH) / "词库-百度300.txt"))
    
    # 添加一些常见网络用语到词典
    jieba.add_word("卧槽")

    print("消息分析-初始化 初始化词库完成")
    my_logger.info(f"消息分析-初始化", "初始化词库完成")


# 在模块加载时初始化
init_jieba()