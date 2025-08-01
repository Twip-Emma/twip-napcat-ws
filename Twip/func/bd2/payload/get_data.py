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

async def delete_user_bindings(user_id: str) -> Tuple[bool, str]:
    """异步删除当前QQ号的所有绑定"""
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None,
        lambda: get_db.delete_user_bindings(user_id)
    )
    if success:
        return True, f"已删除QQ={user_id}的所有绑定"
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