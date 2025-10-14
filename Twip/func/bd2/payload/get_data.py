import aiohttp
import asyncio
from .user_db import get_db
from typing import Dict, Any, Tuple, Optional, List
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))


async def user_bind() -> str:
    return "测试"


async def user_bind(user_id: str, nickname: str) -> Tuple[bool, str]:
    """
    异步绑定用户QQ号和昵称（允许一对多）
    :return: (是否成功, 消息)
    """
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None,
        lambda: get_db.bind_user(user_id, nickname)
    )
    if success:
        return True, f"绑定成功: QQ={user_id}, 昵称={nickname}"
    return False, "绑定失败（可能已存在相同绑定）"

async def get_user_nicknames(user_id: str) -> List[str]:
    """异步查询当前QQ号的所有昵称"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: get_db.get_user_nicknames(user_id)
    )

async def delete_user_bindings(user_id: str, nickname: str = None) -> Tuple[bool, str]:
    """异步删除当前QQ号的所有绑定"""
    loop = asyncio.get_event_loop()
    success = False
    if (nickname is None) :
        success = await loop.run_in_executor(
            None,
            lambda: get_db.delete_user_bindings(user_id)
        )
        if success:
            return True, f"已删除QQ={user_id}的所有绑定"
        return False, "删除失败（数据库错误）"
    else:
        success = await loop.run_in_executor(
            None,
            lambda: get_db.delete_user_bindings_by_nickname(user_id=user_id,nickname=nickname)
        )
        if success:
            return True, f"已删除QQ={user_id}的 {nickname} 的绑定"
        return False, "删除失败（数据库错误）"
    


async def redeem_coupon(user_id: str, coupon_code: str) -> str:
    """
    兑换优惠券（简洁版）
    :return: 直接返回可读的字符串结果，格式：昵称: 消息\n...
    """
    nicknames = get_db.get_user_nicknames(user_id)
    if not nicknames:
        return "该QQ号未绑定任何游戏昵称"

    async with aiohttp.ClientSession() as session:
        tasks = [
            _get_single_redeem_result(session, nickname, coupon_code)
            for nickname in nicknames
        ]
        results = await asyncio.gather(*tasks)

    return "\n".join(results)

async def _get_single_redeem_result(
    session: aiohttp.ClientSession, 
    nickname: str, 
    coupon_code: str
) -> str:
    """
    获取单个昵称的兑换结果（内部方法）
    :return: 格式 "昵称: 消息"
    """
    url = "https://loj2urwaua.execute-api.ap-northeast-1.amazonaws.com/prod/coupon"
    headers = {
        "Content-Type": "application/json",
        "access-control-allow-origin": "https://redeem.bd2.pmang.cloud",
    }
    payload = {
        "appId": "bd2-live",
        "userId": nickname,
        "code": coupon_code,
    }

    try:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json(content_type=None)
            message = data.get("message", "领取成功")
            
            # 韩语错误消息翻译
            if message == "쿠폰 사용 기간이 지났습니다.":
                message = "兑换码已过期"
            elif message == "이미 사용된 쿠폰입니다.":
                message = "兑换码已被使用"
            elif message == "이미 사용한 쿠폰입니다. (키워드)":
                message = "已经使用过的优惠券"
                
            return f"{nickname}: {message}"

    except Exception as e:
        return f"{nickname}: 请求失败({str(e)})"


async def redeem_all_coupons_for_user(user_id: str) -> str:
    """
    为指定用户兑换所有可用兑换码
    :param user_id: 用户ID
    :return: 兑换结果字符串
    """
    nicknames = get_db.get_user_nicknames(user_id)
    if not nicknames:
        return "该QQ号未绑定任何游戏昵称"
    
    # 获取所有兑换码
    coupons = await fetch_redeem_codes()
    if not coupons:
        return "未能获取到任何兑换码"
    
    results = []
    
    for coupon in coupons:
        code = coupon["code"]
        reward = coupon["reward"]
        status = coupon["status"]
        
        # 添加兑换码信息
        results.append(f"兑换码: {code} | 奖励: {reward} | 有效期: {status}")
        
        # 为每个昵称兑换该兑换码
        async with aiohttp.ClientSession() as session:
            tasks = [
                _get_single_redeem_result(session, nickname, code)
                for nickname in nicknames
            ]
            redeem_results = await asyncio.gather(*tasks)
            results.extend(redeem_results)
    
    return "\n".join(results)

async def _get_single_redeem_result(
    session: aiohttp.ClientSession, 
    nickname: str, 
    coupon_code: str
) -> str:
    """
    获取单个昵称的兑换结果（内部方法）
    :return: 格式 "昵称: 消息"
    """
    url = "https://loj2urwaua.execute-api.ap-northeast-1.amazonaws.com/prod/coupon"
    headers = {
        "Content-Type": "application/json",
        "access-control-allow-origin": "https://redeem.bd2.pmang.cloud",
        "referer": "https://redeem.bd2.pmang.cloud/"
    }
    payload = {
        "appId": "bd2-live",
        "userId": nickname,
        "code": coupon_code,
    }
    try:
        async with session.post(url, json=payload, headers=headers) as response:
            data = await response.json(content_type=None)
            message = data.get("message", "兑换成功")
            
            # 韩语错误消息翻译
            if message == "쿠폰 사용 기간이 지났습니다.":
                message = "兑换码已过期"
            elif message == "이미 사용한 쿠폰입니다. (키워드)":
                message = "兑换码已被使用"
                
            return f"{nickname}: {message}"

    except Exception as e:
        return f"{nickname}: 请求失败({str(e)})"


# 需要人工维护
async def fetch_redeem_codes() -> List[Dict]:
    data = get_db.get_valid_coupons()
    resp = []
    if data == []:
        return []
    else:
        for item in data:
            resp.append({
                "code":item[1],
                "reward":item[2],
                "status":str(item[3])
            })
    return resp
    # return [{"code":"BD2RADIO0801","reward":"3抽","status":""},
    #         {"code":"2025BD2AUG","reward":"2抽","status":"2025/9/1"},
    #         {"code":"BD2SDCC2025","reward":"600鑽","status":"2025/8/24"},
    #         {"code":"BD2BW2025","reward":"600鑽","status":"2025/8/11"},
    #         {"code":"BD2RADIO0701","reward":"3抽","status":"2025/8/31"},
    #         {"code":"BD2025SUMMER","reward":"一張酒館的5星招募卷","status":"目前可用"},
    #         {"code":"Waiting4legend","reward":"頂級毒蛇之手","status":"目前可用"}]
    
    # 下面的api获取最新兑换码，但是需要翻墙
    # """获取可用的兑换码列表"""
    # url = "https://thedb2pulse-api.zzz-archive-back-end.workers.dev/redeem"
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(url) as response:
    #         if response.status == 200:
    #             return await response.json()
    #         return []


async def get_coupon_all() -> str:
    resp = "棕色尘埃2有效兑换码\n"
    data = get_db.get_valid_coupons()
    if data == []:
        return "兑换码列表为空"
    else:
        index = 1
        for item in data:
            resp += f"{index}:{item[1]} | {item[2]}\n"
            index += 1
    return resp


async def add_coupon(coupon_code: str, description: str, valid_date_str: str) -> str:
    v_date = "";
    if valid_date_str == "永久":
        v_date = "2999-01-01"
    else:
        v_date = valid_date_str
    resp = get_db.add_coupon(coupon_code, description, v_date)
    if not resp:
        return "添加失败"
    else:
        return "添加成功"


async def delete_coupon(coupon_code: str) -> str:
    resp = get_db.delete_coupon(coupon_code)
    if not resp:
        return "删除失败"
    else:
        return "删除成功"
