from .db_service import add_user_info
import random

async def get_treasure_by_select(user_id:str) -> str:
    index:int = random.randint(1,100)
    if index < 2:
        big_coin_gift:int = random.randint(2000,5000)
        add_user_info(user_id = user_id, count = big_coin_gift)
        return f"恭喜你获得了一个豪华宝箱：\n获得了{big_coin_gift}币"
    elif index < 5:
        big_coin_gift:int = random.randint(1000,2000)
        add_user_info(user_id = user_id, count = big_coin_gift)
        return f"恭喜你获得了一个大宝箱：\n获得了{big_coin_gift}币"
    elif index < 20:
        big_coin_gift:int = random.randint(100,1000)
        add_user_info(user_id = user_id, count = big_coin_gift)
        return f"你捡到一个钱包：\n打开获得了{big_coin_gift}币"
    elif index < 80:
        big_coin_gift:int = random.randint(5,100)
        add_user_info(user_id = user_id, count = big_coin_gift)
        return f"你捡到一个破旧的钱袋：\n打开获得了{big_coin_gift}币"
    else:
        big_coin_gift:int = random.randint(1,5)
        item:str = random.choice(['海草', '石头', '破贝壳', '粪便', '腐朽的木头', '骨头', '海藻', '空瓶子'])
        add_user_info(user_id = user_id, count = big_coin_gift)
        return f"你捡到一{item}：\n回收获得了{big_coin_gift}币"


async def get_treasure_by_add(user_id:str) -> str:
    return ""