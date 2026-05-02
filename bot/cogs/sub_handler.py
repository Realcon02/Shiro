import asyncio
import random
import traceback
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import discord
from aiohttp import ClientConnectorError
from discord.ext import commands, tasks

from bot import Shiro
from bot.core import SITES
from bot.services import DatabaseManager, LibAPI, DiscordUploader
from bot.views import ChapterNotificationView
from config import INTERVAL_CHECKING_NEW_CHAPTERS

# Импорт только для проверки типов (не выполняется при запуске)
if TYPE_CHECKING:
    from asyncpg import Record


def _build_chapter_url(site_id, slug_url, volume, number, branch_id):
    try:
        base = SITES.get(site_id).base_url
    except:
        print(f"Unknown site_id: {site_id}")
        return None

    url = f"{base}/ru/{slug_url}/read/v{volume}/c{number}"

    if branch_id:
        url += f"?bid={branch_id}"

    return url


class SubHandler(commands.Cog):
    """Обработчик подписок"""
    def __init__(self, bot: Shiro) -> None:
        self.bot = bot
        self.lib_api: LibAPI = bot.lib_api
        self.db: DatabaseManager = bot.db
        self.uploader: DiscordUploader = bot.uploader

        self.check_new_chapters_loop.start()

    def cog_unload(self) -> None:
        self.check_new_chapters_loop.cancel()

    # Логика цикла
    @tasks.loop(minutes=INTERVAL_CHECKING_NEW_CHAPTERS)
    async def check_new_chapters_loop(self):
        """Цикл проверки новых глав"""
        await self._check_new_chapters()

    @check_new_chapters_loop.before_loop
    async def before_check_new_chapters(self):
        await self.bot.wait_until_ready()

        now = datetime.now()
        next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        sleep_time = (next_minute - now).total_seconds()
        await asyncio.sleep(sleep_time)

    # Главные обрабатывающие функции
    async def _check_new_chapters(self):
        """Проверка новых глав для всех подписок"""

        try:
            print(f'[{datetime.now()}] Checking new chapters...')

            subscriptions = await self.db.get_all_subscriptions()
            print(f'Found {len(subscriptions)} subscriptions to check')

            for sub in subscriptions:
                await self._process_sub(sub)
                # Небольшая случайная задержка между подписками, чтобы не спамить API
                await asyncio.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            print(f'Error while checking chapters:\n{type(e).__name__}: {e}')

    async def _process_sub(self, sub):
        """Обработка одной подписки"""

        print(f'Начинаю проверку подписки:')
        print(f'({", ".join(map(str, sub.values()))})')

        try:
            guild_subs = await self.db.get_guilds_for_sub(sub['id'])
            if not guild_subs:
                print(f"Sub {sub['id']} has no guilds, removing...")
                await self.db.delete_orphan_sub(sub['id'])
                return

            work_info: Record | None = None
            new_ids = []

            match sub['target_type']:
                case 'works':
                    work_info = await self.db.get_work_info(sub['target_id'])

                    if not work_info:
                        print(f"Warning: Work info not found for sub {sub['id']}")
                        return

                    new_ids = await self.lib_api.get_new_chapter_ids_work(
                        work_info['site_id'],
                        work_info['slug_url'],
                        sub['newest_id_chapter'],
                    )
                case 'teams':
                    pass
                case 'works_teams':
                    pass
                case 'branches_works':
                    pass

            if new_ids:
                print(f'Обнаружены новые главы: {new_ids}')

                thumbnail_url = await self.uploader.get_url_from_libapi(
                    self.lib_api,
                    work_info['slug_url'],
                    work_info['site_id'],
                )

                # Последовательно обрабатываем каждую новую главу
                for new_id in new_ids:
                    try:
                        chapter_info = await self.lib_api.get_chapter_info(
                            work_info['site_id'],
                            work_info['slug_url'],
                            new_id,
                        )
                        chapter_url = _build_chapter_url(
                            work_info['site_id'],
                            work_info['slug_url'],
                            chapter_info['volume'],
                            chapter_info['number'],
                            chapter_info['branch_id'],
                        )

                        for guild_sub in guild_subs:
                            await self._send_notification(
                                guild_sub,
                                work_info,
                                chapter_info,
                                thumbnail_url,
                                chapter_url,
                            )

                        print(f"Notifications sent for chapter {new_id} to {len(guild_subs)} guilds")
                    except Exception as e:
                        print(f"Error processing chapter {new_id} for sub {sub['id']}:\n{type(e).__name__}: {e}")
                        traceback.print_exc()

                # Обновляем ID последней главы в БД
                await self.db.update_sub(sub['id'], max(new_ids))

            else:
                print('Новых глав не обнаружено')
        except ClientConnectorError as e:
            print(f"Network error for sub {sub['id']}:\n{type(e).__name__}: {e}")
            traceback.print_exc()
            return
        except Exception as e:
            print(f"Error processing subscription {sub['id']}:\n{type(e).__name__}: {e}")
            traceback.print_exc()

    async def _send_notification(self, guild_sub, work_info, chapter_info, thumbnail_url, chapter_url):
        """Отправка уведомления на конкретный сервер"""

        try:
            channel = self.bot.get_channel(guild_sub['channel_id'])
            if channel and isinstance(channel, discord.TextChannel):
                # Создаем view с уведомлением
                view = ChapterNotificationView(
                    work_info['rus_name'] or work_info['name'],
                    chapter_info['volume'],
                    chapter_info['number'],
                    chapter_info['name'],
                    thumbnail_url,
                    chapter_url
                )
                await channel.send(view=view)

                print(f'Было отправлено уведомление на:\n'
                      f'  Сервер: {guild_sub['guild_id']}\n'
                      f'  Канал:  {guild_sub['channel_id']}')

        except Exception as e:
            print(f"Error sending a notification to the channel {guild_sub['channel_id']}:\n{type(e).__name__}: {e}")


def setup(bot) -> None:
    bot.add_cog(SubHandler(bot))
