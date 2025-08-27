import asyncpg
from datetime import datetime


class DatabaseManager:
    """Менеджер базы данных"""
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def initialize(self, db_params):
        """Создание пула соединений"""
        self.pool = await asyncpg.create_pool(
            min_size=1, max_size=8, **db_params
        )
        print('[INFO] Database pool initialized')

    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print('[INFO] Database pool closed')

    async def create_sub(self, target_type: str,
                         target_id: int,
                         newest_id_chapter: int) -> None:
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO
                    subscriptions(target_type, target_id, newest_id_chapter, created_at)
                    VALUES ($1, $2, $3, $4)""",
                    target_type, target_id, newest_id_chapter, datetime.now()
                )

    async def check_sub_exists(self, target_type: str, target_id: int) -> bool:
        """Проверка существования подписки"""
        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT EXISTS (SELECT 1 FROM subscriptions WHERE target_type = $1 AND target_id = $2)",
                target_type, target_id
            )