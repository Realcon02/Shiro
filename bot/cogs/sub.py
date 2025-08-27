import discord
from discord.ext import commands
from discord import AutocompleteContext, TextChannel, OptionChoice, option

from bot import Shiro
from bot.services import DatabaseManager, LibAPI


class Subscription(commands.Cog):
    def __init__(self, bot: Shiro) -> None:
        self.bot = bot
        self.lib_api: LibAPI = bot.lib_api
        self.db: DatabaseManager = bot.db

    # Автозаполнения
    async def get_works_auto(self, ctx: AutocompleteContext):
        """Автозаполнение для поиска произведений"""
        site = ctx.options.get('site') or 3
        title = ctx.value

        return await self.lib_api.search_title(site, title)

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
    _site_options = [OptionChoice('RanobeLIB', 3), OptionChoice('MangaLIB', 1)]

    @subscription.command(name='help')
    async def help_sub(self, ctx: discord.ApplicationContext):
        await ctx.respond('В разработке')

    @subscription.command(name='add_of_work',
                          description='Создать подписку типа «Произведение»')
    @option(name='site',
            description='Выберите сайт для поиска (по умолчанию RanobeLIB)',
            input_type=int,
            choices=_site_options)
    @option(name='work',
            description='Поиск произведения',
            input_type=int,
            autocomplete=get_works_auto)
    @option(name='channel',
            description='Выберите текстовый канал, в котором у бота есть необходимые права для отправки уведомлений',
            input_type=discord.TextChannel,
            autocomplete=get_suitable_channels)
    async def add_of_work(self,
                          ctx: discord.ApplicationContext,
                          site: int,
                          work: int,
                          channel: discord.TextChannel):
        await ctx.respond(f'site: {site}\n'
                          f'work: {work}\n'
                          f'channel: {channel}')

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

    @subscription.command(name='list')
    async def list_sub(self, ctx: discord.ApplicationContext):
        await ctx.respond('В разработке')


def setup(bot) -> None:
    bot.add_cog(Subscription(bot))
