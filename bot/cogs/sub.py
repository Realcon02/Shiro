import discord
from discord.ext import commands


class Subscription(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    subscription = discord.SlashCommandGroup(name='sub')

    @subscription.command(name='help')
    async def help_subscription(self, ctx: discord.ApplicationContext):
        pass

    @subscription.command(name='add')
    async def add_subscription(self, ctx: discord.ApplicationContext):
        pass

    @subscription.command(name='delete')
    async def delete_subscription(self, ctx: discord.ApplicationContext):
        pass

    @subscription.command(name='list')
    async def list_subscription(self, ctx: discord.ApplicationContext):
        pass


def setup(bot) -> None:
    bot.add_cog(Subscription(bot))
