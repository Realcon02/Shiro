import asyncpg
from datetime import datetime, timezone


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

    async def add_sub_to_guild(self, sub_id: int, guild_id: int, channel_id: int):
        """Добавление подписки на сервер"""

        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO
                    subscriptions_guilds(subscription_id, guild_id, channel_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (subscription_id, guild_id) DO NOTHING""",
                    sub_id, guild_id, channel_id
                )

    async def create_sub(self, target_type: str, target_id: int, newest_id_chapter: int) -> int:
        """Создание подписки"""

        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetchval("""
                    INSERT INTO
                    subscriptions(target_type, target_id, newest_id_chapter)
                    VALUES ($1, $2, $3)
                    RETURNING id""",
                    target_type, target_id, newest_id_chapter
                )

    async def add_work(self, work_id: int, slug_url: str) -> None:
        """Добавление slug_url произведения в БД"""

        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO
                    works(work_id, slug_url)
                    VALUES ($1, $2)
                    ON CONFLICT (work_id) DO NOTHING""",
                    work_id, slug_url
                )

    async def get_sub_id(self, target_type: str, target_id: int) -> int | None:
        """Получение ID подписки, если она существует"""

        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT id FROM subscriptions
                WHERE target_type = $1 AND target_id = $2""",
                target_type, target_id
            )

    async def check_sub_guild_exists(self, sub_id: int, guild_id: int) -> bool:
        """Проверка существования подписки у сервера"""

        conn: asyncpg.Connection
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT EXISTS
                (SELECT 1 FROM subscriptions_guilds
                WHERE subscription_id = $1 AND guild_id = $2)""",
                sub_id, guild_id
            )