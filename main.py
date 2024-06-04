import discord
from discord.ext import commands
import os  # default module
from dotenv import load_dotenv

from config import *

load_dotenv()  # load all the variables from the env file
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=prefixes, intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user.name} готова!")


@bot.command(name='test')
async def test_prefix(ctx: commands.Context):
    await ctx.send(type(ctx))


@bot.slash_command(name="test-slash")
async def test_slash(ctx: discord.ApplicationContext):
    await ctx.respond("Успешный тест!")
    await ctx.channel.send(type(ctx))


@bot.slash_command(name='ping')
async def ping(ctx: discord.ApplicationContext):
    await ctx.respond(f'Pong! {round(bot.latency * 1000)}ms')


bot.run(os.getenv('TOKEN'))  # run the bot with the token
