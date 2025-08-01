import sqlite3
from typing import Optional, Tuple, List

class Database:
    def __init__(self, db_path: str = "user_bind.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库表（允许一个QQ号绑定多个昵称）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_bind (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    nickname TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, nickname)
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

# 全局数据库实例（单例模式）
get_db = Database()