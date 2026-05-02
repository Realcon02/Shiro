import traceback

import discord
from aiohttp import ClientConnectorError, ServerDisconnectedError
from discord import AutocompleteContext, OptionChoice, option
from discord.ext import commands
from discord.ext.pages import Paginator

from bot import Shiro
from bot.core import SITES, SUB_TYPES
from bot.services import DatabaseManager, LibAPI
from bot.utils.formatters import truncate
from bot.views import SubListView


class Subscription(commands.Cog):
    def __init__(self, bot: Shiro) -> None:
        self.bot = bot
        self.lib_api: LibAPI = bot.lib_api
        self.db: DatabaseManager = bot.db

    # Автозаполнения
    async def get_works_auto(self, ctx: AutocompleteContext):
        """Автозаполнение для поиска произведений"""
        try:
            site = ctx.options.get('site') or 3
            title = ctx.value

            if not title:
                return []

            works: list = await self.lib_api.search_works(site, title)
            return [truncate(w['rus_name'] or w['name']) for w in works[:25]]

        except (ClientConnectorError, ServerDisconnectedError, OSError) as e:
            print(f'[WARN] Network error in autocomplete: {type(e).__name__}')
            return []
        except Exception:
            traceback.print_exc()
            return []

    @staticmethod
    async def get_suitable_channels_auto(ctx: AutocompleteContext):
        """Автозаполнение доступных каналов"""
        guild = ctx.interaction.guild
        user = ctx.interaction.user
        channels = []
        for channel in guild.text_channels:
            bot_perms = channel.permissions_for(guild.me)
            user_perms = channel.permissions_for(user)
            if (
                all([bot_perms.view_channel, bot_perms.send_messages, bot_perms.embed_links]) and
                all([user_perms.view_channel, user_perms.send_messages, user_perms.embed_links]) and 
                ctx.value.lower() in channel.name.lower()
            ):
                channels.append(OptionChoice(
                    name=f'{channel.category.name}: {channel.name}',
                    value=f'ch_{channel.id}',
                ))
        return channels[:25]  # Ограничиваем количество

    async def get_guild_subs_auto(self, ctx: AutocompleteContext):
        """Автозаполнение подписок текущего сервера"""
        try:
            records = await self.db.get_guild_subscriptions(ctx.interaction.guild_id)
            return [
                OptionChoice(
                    name=truncate(f"{SUB_TYPES[r['type']].emoji}: {r['description'] or '—'}"),
                    value=r['sub_id']
                )
                for r in records
                if not ctx.value or ctx.value.lower() in (r['description'] or '').lower()
            ][:25]
        except Exception:
            traceback.print_exc()
            return []

    # Группа команд "sub"
    subscription = discord.SlashCommandGroup(name='sub')
    _site_options = [
        OptionChoice('RanobeLIB', 3),
        OptionChoice('MangaLIB', 1),
    ]

    @subscription.command(name='help')
    async def help_sub(self, ctx: discord.ApplicationContext):
        await ctx.respond('В разработке')

    @subscription.command(
        name='add_work',
        description='Создать подписку типа «Произведение»',
    )
    @option(
        name='site',
        description='Выберите сайт для поиска (по умолчанию RanobeLIB)',
        input_type=int,
        choices=_site_options,
    )
    @option(
        name='work',
        description='Поиск произведения',
        input_type=str,
        autocomplete=get_works_auto,
    )
    @option(
        name='channel',
        description='Выберите текстовый канал, в котором у бота есть необходимые права для отправки уведомлений',
        input_type=str,
        autocomplete=get_suitable_channels_auto,
    )
    async def add_of_work(
            self, ctx: discord.ApplicationContext,
            site: int,
            work: str,
            channel: str,
    ):
        try:
            channel = ctx.guild.get_channel(int(channel.removeprefix('ch_')))
        except ValueError:
            await ctx.respond(
                'Канал не найдено. Воспользуйтесь автодополнением и выберите вариант из списка.',
                ephemeral=True
            )
            return

        try:
            work_info = await self.lib_api.search_work(site, work.rstrip('...'))

            sub_id = await self.db.get_sub_id('works', work_info['id'])
            if not sub_id:
                newest_id_work = await self.lib_api.search_newest_id_chapter_work(site, work_info['slug_url'])
                await self.db.add_work(work_info)

                sub_id = await self.db.create_sub('works', work_info['id'], newest_id_work)
                print(f"Created new subscription with ID: {sub_id}")

            if not await self.db.check_sub_guild_exists(sub_id, ctx.guild.id):
                await self.db.add_sub_to_guild(sub_id, ctx.guild.id, channel.id)
                await ctx.respond('Подписка успешно создана!')
            else:
                await ctx.respond('Данная подписка уже есть на этом сервере')

        except IndexError:
            await ctx.respond(
                'Произведение не найдено. Воспользуйтесь автодополнением и выберите вариант из списка.',
                ephemeral=True
            )
        except (ClientConnectorError, ServerDisconnectedError, OSError) as e:
            print(f"Network error in add_of_work: {e}")
            # Отправляем ответ только если ещё не отправили
            if not ctx.response.is_done():
                await ctx.respond('Ошибка сети. Попробуйте позже.', ephemeral=True)
        except Exception as e:
            print(f"Error in add_of_work:\n{type(e).__name__}: {e}")
            traceback.print_exc()
            if not ctx.response.is_done():
                await ctx.respond('Произошла ошибка при обработке команды.', ephemeral=True)

    @subscription.command(
        name='delete',
        description='Удалить подписку с этого сервера',
    )
    @option(
        name='sub',
        description='Выберите подписку для удаления',
        input_type=int,
        autocomplete=get_guild_subs_auto,
    )
    async def delete_sub(self, ctx: discord.ApplicationContext, sub: int):
        try:
            deleted = await self.db.remove_sub_from_guild(sub, ctx.guild_id)
            if deleted:
                await ctx.respond('Подписка успешно удалена!')
            else:
                await ctx.respond('Такая подписка не найдена на этом сервере.', ephemeral=True)
        except Exception:
            traceback.print_exc()
            await ctx.respond('Ошибка при удалении подписки.', ephemeral=True)

    @subscription.command(
        name='list',
        description='Список подписок этого сервера',
    )
    async def list_sub(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        try:
            records = await self.db.get_guild_subscriptions(ctx.guild_id)
        except Exception:
            traceback.print_exc()
            await ctx.respond('Ошибка при обращении к базе данных.', ephemeral=True)
            return

        subs = []
        for r in records:
            sub_type = f"{SUB_TYPES[r['type']].emoji} {SUB_TYPES[r['type']].name}"

            sub = {
                'title': r['description'],
                'url': f"{SITES.get(r['site_id'], 3).base_url}/ru/book/{r['slug_url']}",
                'sub_type': sub_type,
                'channel_id': r['channel_id']
            }
            subs.append(sub)

        view = SubListView(subs, ctx.guild.name, ctx.author)

        await ctx.respond(view=view)


def setup(bot) -> None:
    bot.add_cog(Subscription(bot))
