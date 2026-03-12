import discord
from discord.ext import commands

from bot import Shiro
from bot.services import LibAPI


class Template(commands.Cog):
    def __init__(self, bot: Shiro) -> None:
        self.bot = bot
        self.lib_api: LibAPI = bot.lib_api

    @commands.command(name='test-prefix')
    async def test_prefix(self, ctx: commands.Context):
        await ctx.reply("Успешный тест!")
        await ctx.send(type(ctx))

    @commands.slash_command(name="test-slash")
    async def test_slash(self, ctx: discord.ApplicationContext):
        await ctx.respond("Успешный тест!")

    '''
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
    '''


def setup(bot) -> None:
    bot.add_cog(Template(bot))
