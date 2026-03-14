import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks

from bot import Shiro
from bot.services import DatabaseManager, LibAPI
from config import interval_checking_new_chapters

# Импорт только для проверки типов (не выполняется при запуске)
if TYPE_CHECKING:
    from asyncpg import Record


class SubHandler(commands.Cog):
    """Обработчик подписок"""

    def __init__(self, bot: Shiro) -> None:
        self.bot = bot
        self.lib_api: LibAPI = bot.lib_api
        self.db: DatabaseManager = bot.db

        self.check_new_chapters_loop.start()

    def cog_unload(self) -> None:
        self.check_new_chapters_loop.cancel()

    # Логика цикла
    @tasks.loop(minutes=interval_checking_new_chapters)
    async def check_new_chapters_loop(self):
        """Цикл проверки новых глав"""

        await self.check_new_chapters()

    @check_new_chapters_loop.before_loop
    async def before_check_new_chapters(self):
        await self.bot.wait_until_ready()

        now = datetime.now()
        next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        sleep_time = (next_minute - now).total_seconds()
        await asyncio.sleep(sleep_time)

    # Главные обрабатывающие функции
    async def check_new_chapters(self):
        """Проверка новых глав для всех подписок"""

        try:
            print(f'[{datetime.now()}] Checking new chapters...')

            subscriptions = await self.db.get_all_subscriptions()
            print(f'Found {len(subscriptions)} subscriptions to check')

            for sub in subscriptions:
                await self.process_sub(sub)

        except Exception as e:
            print(f'Error while checking chapters:\n{type(e).__name__}: {e}')

    async def process_sub(self, sub):
        """Обработка одной подписки"""

        # Вопрос:
        # Стоит ли создавать 2 функции, одна из которых получает slug_url для поиска newest_id_chapter,
        # а вторая в случае нахождения более нового id забирает name и rus_name
        # Проблема в том, что придётся городить 2 ОДИНАКОВЫХ match. Типа это будет выглядеть нагромождённо, некрасиво.
        # Ну либо вложить if в match, из-за чего if'ов станет АЖ 4 ОДИНАКОВЫХ

        # Мнение:
        # Мне так-то похуй, больше или меньше инфы из БД за раз запрашивать будут,
        # если это практически неразличимо в плане производительности

        print(f'Начинаю проверку подписки:')
        # print(f'({sub['id']}, {sub['target_type']}, {sub['target_id']}, {sub['newest_id_chapter']}, {sub['created_at']})')
        print(f'({", ".join(map(str, sub.values()))})')

        try:
            newest_chapter_id: int | None = None
            work_info: Record | None = None

            match sub['target_type']:
                case 'works':
                    work_info = await self.db.get_work_info(sub['target_id'])

                    if not work_info:
                        print(f"Warning: Work info not found for sub {sub['id']}")
                        return

                    newest_chapter_id = await self.lib_api.search_newest_id_chapter_work(work_info['slug_url'])
                case 'teams':
                    pass
                case 'works_teams':
                    pass
                case 'branches_works':
                    pass

            if newest_chapter_id and newest_chapter_id > (old_chapter_id := sub['newest_id_chapter']):
                print(f'Обнаружена глава с более новым id: {newest_chapter_id}')

                # Получаем сервера с этой подпиской
                guild_subs = await self.db.get_guilds_for_sub(sub['id'])

                # Получаем список ID новых глав
                new_ids = await self.lib_api.get_new_chapter_ids_work(work_info['slug_url'], old_chapter_id)

                # Последовательно обрабатываем каждую новую главу
                for new_id in new_ids:
                    try:
                        # ОПТИМИЗАЦИЯ: Получаем инфо о главе 1 раз, а не на каждый сервер
                        chapter_info = await self.lib_api.get_chapter_info(work_info['slug_url'], new_id)

                        for guild_sub in guild_subs:
                            await self.send_notification(guild_sub, work_info, chapter_info)

                        print(f"Notifications sent for chapter {new_id} to {len(guild_subs)} guilds")

                    except Exception as e:
                        print(f"Error processing chapter {new_id} for sub {sub['id']}:\n{type(e).__name__}: {e}")

                # Обновляем ID последней главы в БД
                await self.db.update_sub(sub['id'], newest_chapter_id)

            else:
                print('Новых глав не обнаружено')

        except Exception as e:
            print(f"Error processing subscription {sub['id']}:\n{type(e).__name__}: {e}")

    async def send_notification(self, guild_sub, work_info, chapter_info):
        """Отправка уведомления на конкретный сервер"""

        try:
            channel = self.bot.get_channel(guild_sub['channel_id'])
            if channel and isinstance(channel, discord.TextChannel):
                # Создаем embed с уведомлением
                embed = discord.Embed(
                    title="Вышла новая глава!",
                    description=f"**{work_info['name']}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Том", value=chapter_info['volume'], inline=True)
                embed.add_field(name="Глава", value=chapter_info['number'], inline=True)
                embed.add_field(name="Название", value=chapter_info['name'] or "Без названия", inline=True)
                embed.set_footer(text="Приятного чтения!")

                await channel.send(embed=embed)

                print(f'Было отправлено уведомление на:\n'
                      f'  Сервер: {guild_sub['guild_id']}\n'
                      f'  Канал:  {guild_sub['channel_id']}')

        except Exception as e:
            print(f"Error sending a notification to the channel {guild_sub['channel_id']}:\n{type(e).__name__}: {e}")


def setup(bot) -> None:
    bot.add_cog(SubHandler(bot))
