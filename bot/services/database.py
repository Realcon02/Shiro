import asyncio

from asyncpg import Connection, Pool, create_pool

from bot.core import WorkInfo, SubRecord, Subscription, WorkSearchResult, GuildSub


class DatabaseManager:
    """Менеджер базы данных"""
    def __init__(self):
        self.pool: Pool | None = None

    async def initialize(self, db_params):
        """Создание пула соединений"""
        retries = 10
        delay = 2

        for attempt in range(1, retries + 1):
            try:
                self.pool = await create_pool(  # noqa
                    min_size=1,
                    max_size=8,
                    timeout=5,
                    **db_params
                )
                print('[INFO] Database pool initialized')
                return

            except Exception as e:
                print(f'[DB] Attempt {attempt}/{retries} failed: {e}')

                if attempt == retries:
                    raise

                await asyncio.sleep(delay)

    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            print('[INFO] Database pool closed')

    # Операции с подписками
    async def create_sub(self, target_type: str, target_id: int, newest_id_chapter: int) -> int:
        """Создание подписки"""

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                return await conn.fetchval("""
                    INSERT INTO
                    subscriptions(target_type, target_id, newest_id_chapter)
                    VALUES ($1, $2, $3)
                    RETURNING id
                """, target_type, target_id, newest_id_chapter)

    async def add_sub_to_guild(self, sub_id: int, guild_id: int, channel_id: int):
        """Добавление подписки на сервер"""

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO
                    subscriptions_guilds(subscription_id, guild_id, channel_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (subscription_id, guild_id) DO NOTHING
                """, sub_id, guild_id, channel_id)

    async def update_sub(self, sub_id: int, newest_chapter_id: int):
        """Обновление подписки, т.е. обновление ID новейшей главы"""

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    UPDATE subscriptions
                    SET newest_id_chapter = $1
                    WHERE id = $2
                """, newest_chapter_id, sub_id)

    async def check_sub_guild_exists(self, sub_id: int, guild_id: int) -> bool:
        """Проверка существования подписки у сервера"""

        conn: Connection
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT EXISTS
                (SELECT 1 FROM subscriptions_guilds
                WHERE subscription_id = $1 AND guild_id = $2)
            """, sub_id, guild_id)

    async def remove_sub_from_guild(self, sub_id: int, guild_id: int) -> bool:
        """Удаляет подписку с сервера. Возвращает True, если запись была удалена."""

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                result = await conn.execute("""
                    DELETE FROM subscriptions_guilds
                    WHERE subscription_id = $1 AND guild_id = $2
                """, sub_id, guild_id)
                return result == 'DELETE 1'

    async def delete_orphan_sub(self, sub_id: int) -> None:
        """Удаляет подписку, у которой нет серверов"""

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    DELETE FROM subscriptions WHERE id = $1
                """, sub_id)

    # Операции с метаданными
    async def add_work(self, work: WorkSearchResult) -> None:
        """Добавление информации о произведении в БД"""

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO
                    works(work_id, site_id, name, rus_name, slug_url)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (work_id) DO NOTHING
                """, work.id, work.site_id, work.name, work.rus_name, work.slug_url)

    # Операции чтения
    async def get_all_subscriptions(self) -> list[Subscription]:
        """Получение всех подписок"""

        conn: Connection
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM subscriptions")
            return [Subscription(**row) for row in rows]

    async def get_sub_id(self, target_type: str, target_id: int) -> int | None:
        """Получение ID подписки, если она существует"""

        conn: Connection
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT id FROM subscriptions
                WHERE target_type = $1 AND target_id = $2
            """, target_type, target_id)

    async def get_work_info(self, target_id: int) -> WorkInfo | None:
        """Получение информации о произведении"""

        conn: Connection
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT site_id, name, rus_name, slug_url FROM works
                WHERE work_id = $1
            """, target_id)
            return WorkInfo(**row) if row else None

    async def get_guilds_for_sub(self, sub_id: int) -> list[GuildSub]:
        """Возвращает список серверов, имеющих данную подписку"""

        conn: Connection
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT guild_id, channel_id FROM subscriptions_guilds
                WHERE subscription_id = $1
            """, sub_id)
            return [GuildSub(**row) for row in rows]

    async def get_guild_subscriptions(self, guild_id: int) -> list[SubRecord]:
        """
        Получение всех подписок сервера с человекочитаемым описанием.
        Один JOIN-запрос покрывает все 4 типа подписки.
        """
        conn: Connection
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT
                    s.id,
                    s.target_type AS type,
                    sg.channel_id,
                    CASE s.target_type
                        WHEN 'works'          THEN w.site_id
                        WHEN 'branches_works' THEN bw_work.site_id
                        WHEN 'works_teams'    THEN wt_work.site_id
                        -- teams: NULL по умолчанию, ELSE не нужен
                    END AS site_id,
                    CASE s.target_type
                        WHEN 'works'          THEN w.slug_url
                        WHEN 'teams'          THEN t.slug_url
                        WHEN 'branches_works' THEN bw_work.slug_url
                        WHEN 'works_teams'    THEN wt_work.slug_url
                    END AS slug_url,
                    CASE s.target_type
                        WHEN 'works' THEN
                            COALESCE(w.rus_name, w.name)
                        WHEN 'teams' THEN
                            t.name
                        WHEN 'branches_works' THEN
                            'Ветка №' || bw.branch_number || ' — ' ||
                            COALESCE(bw_work.rus_name, bw_work.name)
                        WHEN 'works_teams' THEN
                            wt_team.name || ' — ' ||
                            COALESCE(wt_work.rus_name, wt_work.name)
                    END AS description
                FROM subscriptions_guilds sg
                JOIN subscriptions s
                    ON s.id = sg.subscription_id
                -- works: target_id = work_id
                LEFT JOIN works w
                    ON s.target_type = 'works'
                    AND w.work_id = s.target_id
                -- teams: target_id = team_id
                LEFT JOIN teams t
                    ON s.target_type = 'teams'
                    AND t.team_id = s.target_id
                -- branches_works: target_id = branch_id
                LEFT JOIN branches_works bw
                    ON s.target_type = 'branches_works'
                    AND bw.branch_id = s.target_id
                LEFT JOIN works bw_work
                    ON bw.work_id = bw_work.work_id
                -- works_teams: target_id = works_teams.id
                LEFT JOIN works_teams wt
                    ON s.target_type = 'works_teams'
                    AND wt.id = s.target_id
                LEFT JOIN works wt_work
                    ON wt.work_id = wt_work.work_id
                LEFT JOIN teams wt_team
                    ON wt.team_id = wt_team.team_id
                WHERE sg.guild_id = $1
                ORDER BY s.target_type, s.id
            """, guild_id)
            return [SubRecord(**row) for row in rows]
