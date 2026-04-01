from asyncpg import Connection, Pool, Record, create_pool


class DatabaseManager:
    """Менеджер базы данных"""
    def __init__(self):
        self.pool: Pool | None = None

    async def initialize(self, db_params):
        """Создание пула соединений"""
        self.pool = await create_pool(
            min_size=1, max_size=8, **db_params
        )
        print('[INFO] Database pool initialized')

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
                    RETURNING id""",
                    target_type, target_id, newest_id_chapter
                )

    async def add_sub_to_guild(self, sub_id: int, guild_id: int, channel_id: int):
        """Добавление подписки на сервер"""

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO
                    subscriptions_guilds(subscription_id, guild_id, channel_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (subscription_id, guild_id) DO NOTHING""",
                    sub_id, guild_id, channel_id
                )

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
                WHERE subscription_id = $1 AND guild_id = $2)""",
                sub_id, guild_id
            )

    # Операции с метаданными
    async def add_work(self, work_info: dict) -> None:
        """Добавление информации о произведении в БД"""

        work_id, name, rus_name, slug_url = work_info.values()

        conn: Connection
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("""
                    INSERT INTO
                    works(work_id, name, rus_name, slug_url)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (work_id) DO NOTHING""",
                    work_id, name, rus_name, slug_url
                )

    # Операции чтения
    async def get_all_subscriptions(self) -> list[Record]:
        """Получение всех подписок"""

        conn: Connection
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT * FROM subscriptions
            """)

    async def get_sub_id(self, target_type: str, target_id: int) -> int | None:
        """Получение ID подписки, если она существует"""

        conn: Connection
        async with self.pool.acquire() as conn:
            return await conn.fetchval("""
                SELECT id FROM subscriptions
                WHERE target_type = $1 AND target_id = $2""",
                target_type, target_id
            )

    async def get_work_info(self, target_id: int) -> Record:
        """Получение информации о произведении"""

        conn: Connection
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT name, rus_name, slug_url FROM works
                WHERE work_id = $1""",
                target_id
            )

    async def get_guilds_for_sub(self, sub_id: int) -> list[Record]:
        """Возвращает список серверов, имеющих данную подписку"""

        conn: Connection
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT guild_id, channel_id FROM subscriptions_guilds
                WHERE subscription_id = $1
            """, sub_id)

    async def get_guild_subscriptions(self, guild_id: int) -> list[Record]:
        """
        Получение всех подписок сервера с человекочитаемым описанием.
        Один JOIN-запрос покрывает все 4 типа подписки.
        """
        conn: Connection
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT
                    s.id          AS sub_id,
                    s.target_type AS type,
                    sg.channel_id,
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