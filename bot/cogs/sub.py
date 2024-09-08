import discord
from discord.ext import commands
from discord import OptionChoice, ChannelType

from ..subscription.adding import get_titles_auto, get_team_or_branch_auto, sub_add_team
from ..subscription.parser import search_last_chapter


class Subscription(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    subscription = discord.SlashCommandGroup(name='sub')

    @subscription.command(name='help')
    async def help_sub(self, ctx: discord.ApplicationContext):
        pass

    @subscription.command(name='add')
    @discord.option('channel', channel_types=[ChannelType.text])
    @discord.option('site', input_type=int, choices=[OptionChoice('RanobeLIB', 3), OptionChoice('MangaLIB', 1)])
    @discord.option('type_sub', input_type=str, choices=['Team', 'Branch'])
    @discord.option('title', input_type=str, autocomplete=get_titles_auto)
    @discord.option('team_or_branch', input_type=int, autocomplete=get_team_or_branch_auto)
    async def add_sub(self,
                      ctx: discord.ApplicationContext,
                      channel: discord.TextChannel,
                      site: int,
                      type_sub: str,
                      title: str,
                      team_or_branch: int
                      ):
        if type_sub == 'Team':
            last_chapter_id = search_last_chapter(title, team_or_branch)
            sub_add_team(last_chapter_id)
            await ctx.respond(f'{channel.mention}\n{site}\n{type_sub}\n{title}\n{team_or_branch}\n\n{last_chapter_id}')

    @subscription.command(name='delete')
    async def delete_sub(self, ctx: discord.ApplicationContext):
        pass

    @subscription.command(name='list')
    async def list_sub(self, ctx: discord.ApplicationContext):
        pass


def setup(bot) -> None:
    bot.add_cog(Subscription(bot))
