import discord
from discord.ext import commands


class Subscription(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    subscription = discord.SlashCommandGroup(name='subscription')

    @subscription.command(name='add')
    async def add_subscription(self):
        pass


def setup(bot) -> None:
    bot.add_cog(Subscription(bot))
