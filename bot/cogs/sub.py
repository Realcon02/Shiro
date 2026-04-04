import traceback

import discord
from aiohttp import ClientConnectorError, ServerDisconnectedError
from discord import AutocompleteContext, TextChannel, OptionChoice, option
from discord.ext import commands
from discord.ext.pages import Paginator

from bot import Shiro
from bot.services import DatabaseManager, LibAPI
from bot.utils.embeds import build_sub_pages
from bot.utils.formatters import truncate


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
    async def get_suitable_channels(ctx: AutocompleteContext):
        """
        Автозаполнение доступных каналов
        НЕ ДОДЕЛАНА
        """
        channels = []
        for channel in ctx.bot.get_all_channels():
            if isinstance(channel, TextChannel):
                perms = channel.permissions_for(channel.guild.me)
                if perms.send_messages and perms.embed_links:
                    channels.append(discord.OptionChoice(
                        f"#{channel.name} ({channel.guild.name})",
                        channel.id
                    ))
        return channels[:25]  # Ограничиваем количество

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
        description='Создать подписку типа «Произведение»'
    )
    @option(
        name='site',
        description='Выберите сайт для поиска (по умолчанию RanobeLIB)',
        input_type=int,
        choices=_site_options
    )
    @option(
        name='work',
        description='Поиск произведения',
        input_type=str,
        autocomplete=get_works_auto
    )
    @option(
        name='channel',
        description='Выберите текстовый канал, в котором у бота есть необходимые права для отправки уведомлений',
        input_type=TextChannel,
        autocomplete=get_suitable_channels
    )
    async def add_of_work(
            self,ctx: discord.ApplicationContext,
            site: int,
            work: str,
            channel: TextChannel
    ):
        try:
            work_info = await self.lib_api.search_work(site, work.rstrip('...'))

            sub_id = await self.db.get_sub_id('works', work_info['id'])
            if not sub_id:
                newest_id_work = await self.lib_api.search_newest_id_chapter_work(work_info['slug_url'])
                await self.db.add_work(work_info)

                sub_id = await self.db.create_sub('works', work_info['id'], newest_id_work)
                print(f"Created new subscription with ID: {sub_id}")

            if not await self.db.check_sub_guild_exists(sub_id, ctx.guild.id):
                await self.db.add_sub_to_guild(sub_id, ctx.guild.id, channel.id)
                await ctx.respond('Подписка успешно создана!')
            else:
                await ctx.respond('Данная подписка уже есть на этом сервере')

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

        # await ctx.send(f'> Информация:\n'
        #                f'Сайт: {site}\n'
        #                f'Произведение: {work}\n'
        #                f'Канал: {channel.mention}\n'
        #                f'ID работы: {id_work}\n'
        #                f'URL слаг: {slug_url_work}\n'
        #                f'ID подписки: {sub_id}')

    # @subscription.command(name='add')
    # @option('channel', channel_types=[ChannelType.text])
    # @option('site', input_type=int, choices=)
    # @option('type_sub', input_type=str, choices=['Team', 'Branch'])
    # @option('title', input_type=str, autocomplete=get_titles_auto)
    # @option('team_or_branch', input_type=int, autocomplete=get_team_or_branch_auto)
    # async def add_sub(self,
    #                   ctx: discord.ApplicationContext,
    #                   channel: discord.TextChannel,
    #                   site: int,
    #                   type_sub: str,
    #                   title: str,
    #                   team_or_branch: int
    #                   ):
    #     if type_sub == 'Team':
    #         last_chapter_id = search_last_chapter(title, team_or_branch)
    #         sub_add_team(last_chapter_id)
    #         await ctx.respond(f'{channel.mention}\n{site}\n{type_sub}\n{title}\n{team_or_branch}\n\n{last_chapter_id}')

    @subscription.command(name='delete')
    async def delete_sub(self, ctx: discord.ApplicationContext):
        await ctx.respond('В разработке')

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

        pages = build_sub_pages(records, ctx.guild.name)
        paginator = Paginator(pages=pages)
        await paginator.respond(ctx.interaction)


def setup(bot) -> None:
    bot.add_cog(Subscription(bot))
