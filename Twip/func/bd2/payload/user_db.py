import sqlite3
import datetime
from typing import Optional, Tuple, List

class Database:
    def __init__(self, db_path: str = "user_bind.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表（允许一个QQ号绑定多个昵称）"""
        with sqlite3.connect(self.db_path) as conn:
            # 用户绑定表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_bind (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    nickname TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, nickname)
                )
            """)
            # 兑换码表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coupons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coupon_code TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    valid_until DATETIME NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)

    def bind_user(self, user_id: str, nickname: str) -> bool:
        """绑定用户（允许一个QQ号绑定多个昵称）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO user_bind (user_id, nickname) VALUES (?, ?)",
                    (user_id, nickname)
                )
            return True
        except sqlite3.IntegrityError:
            return False  # 忽略重复绑定错误
        except sqlite3.Error:
            return False  # 其他数据库错误

    def get_user_nicknames(self, user_id: str) -> List[str]:
        """查询当前QQ号绑定的所有昵称"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nickname FROM user_bind WHERE user_id=?",
                (user_id,)
            )
            return [row[0] for row in cursor.fetchall()]

    def delete_user_bindings(self, user_id: str) -> bool:
        """删除当前QQ号的所有绑定关系（物理删除）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM user_bind WHERE user_id=?",
                    (user_id,)
                )
            return True
        except sqlite3.Error:
            return False
        
    def add_coupon(self, coupon_code: str, description: str, valid_date_str: str):
        """新增一个兑换码
        Args:
            coupon_code: 兑换码字符串
            description: 兑换码说明
            valid_date_str: 有效日期字符串，格式yyyy-MM-dd
        """
        try:
            valid_date = datetime.strptime(valid_date_str, "%Y-%m-%d").date()
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO coupons (coupon_code, description, valid_until) VALUES (?, ?, ?)",
                    (coupon_code, description, valid_date)
                )
                return True
        except sqlite3.IntegrityError:
            print(f"兑换码 {coupon_code} 已存在")
            return False
        except ValueError:
            print(f"日期格式错误，应为 yyyy-MM-dd: {valid_date_str}")
            return False
    
    def get_valid_coupons(self):
        """获取当前有效的兑换码列表
        Returns:
            list: 包含所有有效兑换码的元组列表，每个元组代表一行记录
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM coupons WHERE valid_until >= ? AND is_active = 1 ORDER BY valid_until",
                (current_date,)
            )
            return cursor.fetchall()
    
    def delete_coupon(self, coupon_code: str):
        """删除一个兑换码
        Args:
            coupon_code: 要删除的兑换码
        Returns:
            bool: 是否成功删除
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM coupons WHERE coupon_code = ?",
                (coupon_code,)
            )
            return cursor.rowcount > 0

# 全局数据库实例（单例模式）
get_db = Database()