import MySQLdb
from typing import Any, Tuple, List, Dict, Union, Optional
import random

from tool.utils import db


def add_bottle(user_id: str, content: str) -> bool:
    try:
        sql = "INSERT INTO `qqbot`.`bottle_info` (`create_time`, `update_time`, `user_id`, `content`) VALUES (NOW(), NOW(), %s, %s)"
        args = (f'{user_id}', f'{content}')
        db.sql_dml(sql, args)
        return True
    except:
        return False


def select_bottle() -> List[Tuple]:
    try:
        sql1 = "SELECT count(*) FROM bottle_info"
        resp1:list = db.sql_dql(sql1)
        count:int = resp1[0][0]
        target:int = random.randint(1, count)
        
        sql2 = "SELECT user_id, content FROM bottle_info WHERE id = %s"
        args = (target,)
        return db.sql_dql(sql2, args)[0]
    except:
        return False
