import discord
from discord.ext import commands, bridge


class Template(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name='test-prefix')
    async def test_prefix(self, ctx):
        await ctx.send("Успешный тест!")
        await ctx.send(type(ctx))

    @commands.slash_command(name="test-slash")
    async def test_slash(self, ctx):
        await ctx.send("Успешный тест!")
        await ctx.channel.send(type(ctx))

    @bridge.bridge_command(name='test-bridge')
    async def test_bridge(self, ctx: bridge.context.BridgeApplicationContext):
        await ctx.respond("Успешный тест!")
        await ctx.channel.send(type(ctx))


def setup(bot) -> None:
    bot.add_cog(Template(bot))
