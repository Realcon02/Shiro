import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.slash_command(name='ping', description="Отправляет данные о задержке бота")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond(f'Pong! {round(ctx.bot.latency * 1000)}ms')
        # await ctx.channel.send(type(ctx))


def setup(bot) -> None:
    bot.add_cog(General(bot))
