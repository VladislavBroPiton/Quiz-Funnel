import asyncpg
import logging
from datetime import date, time, datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self, dsn: str):
        self.pool = await asyncpg.create_pool(dsn)
        # Таблицы создадим здесь же
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS quiz_results (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    experience TEXT,
                    trading_style TEXT,
                    goal TEXT,
                    risk_level TEXT,
                    name TEXT,
                    phone TEXT,
                    result_type TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            # таблица админов
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id BIGINT PRIMARY KEY
                )
            ''')
        logger.info("Database pool created and tables initialized")

    async def add_user(self, user_id: int, username: str):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users (user_id, username) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET username=$2",
                user_id, username
            )

    async def save_quiz_result(self, user_id: int, data: dict) -> int:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO quiz_results (user_id, experience, trading_style, goal, risk_level, name, phone, result_type)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id""",
                user_id,
                data.get('experience'),
                data.get('trading_style'),
                data.get('goal'),
                data.get('risk_level'),
                data.get('name'),
                data.get('phone'),
                data.get('result_type')
            )
            return row['id']

    async def get_quiz_results(self, limit: int = 50) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT q.*, u.username FROM quiz_results q JOIN users u ON q.user_id = u.user_id
                   ORDER BY created_at DESC LIMIT $1""",
                limit
            )
            return [dict(r) for r in rows]

    async def get_quiz_stats(self):
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM quiz_results")
            # распределение по типам трейдеров
            by_type = await conn.fetch("SELECT result_type, COUNT(*) as count FROM quiz_results GROUP BY result_type ORDER BY count DESC")
            # средний опыт
            avg_exp = await conn.fetchval("SELECT COUNT(*) FILTER (WHERE experience = 'experienced') * 100 / NULLIF(COUNT(*),0) FROM quiz_results")
            return {
                'total': total,
                'by_type': [dict(r) for r in by_type],
                'experienced_percent': avg_exp or 0
            }

    # Администраторы
    async def is_admin(self, user_id: int) -> bool:
        async with self.pool.acquire() as conn:
            return await conn.fetchval("SELECT EXISTS(SELECT 1 FROM admins WHERE user_id=$1)", user_id)

    async def add_admin(self, user_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO admins (user_id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)
