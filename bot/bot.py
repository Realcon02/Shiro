import discord
from discord.ext import commands
import os  # default module
from dotenv import load_dotenv

import config

'''
Есть три разновидности ботов:
1. discord.Client - самый базовый бот, умеет "слушать" события и всё. Команды недоступны.
2. discord.ext.commands.Bot - обычный бот, умеет то же, что и первый, но ему также доступны 
команды с префиксами и косой чертой.
3. discord.ext.bridge.Bot - продвинутый бот, умеет то же, что и остальные, но также может 
выполнять гибридные команды (префикс и черта вместе).
'''


class Shiro(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned_or(*config.prefixes),
            intents=intents
        )

        load_dotenv()
        self._TOKEN = os.getenv('TOKEN')

    def setup(self):
        for file in os.listdir(f'{os.path.realpath(os.path.dirname(__file__))}/cogs'):
            if file.endswith('.py'):
                extension = file[:-3]
                try:
                    self.load_extension(f"bot.cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(
                        f"Failed to load extension '{extension}'\n{exception}"
                    )

    def run(self):
        print('Running Bot')
        super().run(self._TOKEN)

    async def on_ready(self):
        print(f"{self.user.name} готова!")
