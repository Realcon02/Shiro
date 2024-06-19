import discord
from discord.ext import commands, bridge


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @bridge.bridge_command(name='ping')
    async def ping(self, ctx: bridge.context.BridgeApplicationContext):
        await ctx.respond(f'Pong! {round(ctx.bot.latency * 1000)}ms')
        await ctx.channel.send(type(ctx))


def setup(bot) -> None:
    bot.add_cog(General(bot))
