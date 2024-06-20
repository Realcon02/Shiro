import discord
from random import randint
from discord.ext import commands, bridge


class Info(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    _list_images = [
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-1.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-53.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-52.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-50.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-49.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-64.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-63.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-39.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-42.gif",
        "https://aniyuki.com/wp-content/uploads/2022/01/aniyuki-anime-girl-crying-gifs-43.gif"
    ]

    info = discord.SlashCommandGroup(name='info')

    @info.command(name='avatar')
    async def view_avatar(self, ctx: bridge.context.BridgeApplicationContext, member: discord.Member):
        user = member.name
        image = member.avatar.url

        embed = discord.Embed(
            title=f'Аватар {user}'
        )
        embed.set_image(url=image)

        await ctx.respond(embed=embed)

    @info.command(name='banner')
    async def view_banner(self, ctx: bridge.context.BridgeApplicationContext, member: discord.Member):
        user = member.name
        image = (await self.bot.fetch_user(member.id)).banner or self._list_images[
            randint(0, len(self._list_images) - 1)]

        embed = discord.Embed(
            title=f'Баннер {user}' if image not in self._list_images else f'У {user} нет баннера'
        )
        embed.set_image(url=image)

        await ctx.respond(embed=embed)


def setup(bot) -> None:
    bot.add_cog(Info(bot))
