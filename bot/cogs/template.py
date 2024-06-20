import discord
from discord.ext import commands, bridge


class Template(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name='test-prefix')
    async def test_prefix(self, ctx: bridge.context.BridgeExtContext):
        await ctx.reply("Успешный тест!")
        await ctx.send(type(ctx))

    @commands.slash_command(name="test-slash")
    async def test_slash(self, ctx: bridge.context.BridgeApplicationContext):
        await ctx.respond("Успешный тест!")
        await ctx.send(type(ctx))

    @bridge.bridge_command(name='test-bridge')
    async def test_bridge(self, ctx: bridge.context.BridgeApplicationContext):
        """
        При вызове через префикс тип ctx - bridge.context.BridgeExtContext
        При вызове через черту тип ctx - bridge.context.BridgeApplicationContext
        :param ctx:
        :return:
        """
        await ctx.respond("Успешный тест!")
        await ctx.send(type(ctx))


def setup(bot) -> None:
    bot.add_cog(Template(bot))
