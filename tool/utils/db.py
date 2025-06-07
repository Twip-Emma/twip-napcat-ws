import MySQLdb
from typing import Any, Tuple, List, Dict, Union, Optional
from contextlib import contextmanager
from Twip import DB_URL, DB_CARD, DB_PASS, DB_LIB
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dbutils.persistent_db import PersistentDB
import MySQLdb

# 创建连接池
pool = PersistentDB(
    creator=MySQLdb,
    host=DB_URL,
    user=DB_CARD,
    password=DB_PASS,
    database=DB_LIB,
    charset='utf8mb4',
    autocommit=False
)

@contextmanager
def get_db_connection():
    """从连接池获取连接"""
    conn = pool.connection()
    try:
        yield conn
    finally:
        conn.close()  # 实际是返还给连接池

def sql_dql(sql: str, params: Optional[Union[Tuple, Dict]] = None) -> List[Tuple]:
    """
    执行查询语句(DQL)
    
    :param sql: SQL查询语句
    :param params: 查询参数(可选)
    :return: 查询结果列表
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params or ())
                return cursor.fetchall()
    except MySQLdb.Error as e:
        logger.error(f"查询执行失败: {e}\nSQL: {sql}\nParams: {params}")
        return []
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return []

def sql_dml(sql: str, params: Optional[Union[Tuple, Dict]] = None) -> int:
    """
    执行数据操作语句(DML)
    
    :param sql: SQL操作语句
    :param params: 操作参数(可选)
    :return: 影响的行数
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                affected_rows = cursor.execute(sql, params or ())
                conn.commit()
                return affected_rows
    except MySQLdb.Error as e:
        logger.error(f"操作执行失败: {e}\nSQL: {sql}\nParams: {params}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return 0
    except Exception as e:
        logger.error(f"未知错误: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return 0

def sql_dml_many(sql: str, params_list: List[Union[Tuple, Dict]]) -> int:
    """
    批量执行DML操作
    
    :param sql: SQL操作语句
    :param params_list: 参数列表
    :return: 影响的总行数
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                total_rows = 0
                for params in params_list:
                    total_rows += cursor.execute(sql, params)
                conn.commit()
                return total_rows
    except MySQLdb.Error as e:
        logger.error(f"批量操作失败: {e}\nSQL: {sql}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return 0