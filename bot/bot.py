import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from .services import DatabaseManager, LibAPI
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

        db_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
        self._DB_PARAMS = db_params
        self.db: DatabaseManager | None = None
        self.lib_api: LibAPI | None = None

    async def setup(self):
        self.db = DatabaseManager()
        await self.db.initialize(self._DB_PARAMS)

        self.lib_api = LibAPI()
        await self.lib_api.initialize()

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

    async def start(self):
        print('Running bot...')
        await super().start(self._TOKEN)

    async def close(self):
        if self.db:
            await self.db.close()
        if self.lib_api:
            await self.lib_api.close()
        await super().close()

    async def on_ready(self):
        print(f"{self.user.name} is ready!")
