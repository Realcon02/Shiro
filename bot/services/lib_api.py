import aiohttp
from aiohttp import ClientSession
from urllib.parse import quote
from discord import OptionChoice


class LibAPI:
    """Асинхронный клиент для работы с API RanobeLIB и MangaLIB"""
    def __init__(self):
        self.base_url = 'https://api.cdnlibs.org/api/'
        self.session: ClientSession | None = None

    async def initialize(self):
        """Инициализация сессии"""
        self.session = aiohttp.ClientSession(self.base_url)
        print('[INFO] Session initialized')

    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None
            print('[INFO] Session closed')

    async def search_title(self, site_id: int, title_name: str) -> list[OptionChoice]:
        url = 'manga'
        params = {'q': title_name, 'site_id[]': site_id}

        async with self.session.get(url=url, params=params) as resp:
            titles = (await resp.json())['data']

            total = []
            for title in titles:
                name_title = title['rus_name'] or title['name']
                total.append(OptionChoice(name_title if len(name_title) <= 100 else name_title[:97] + '...', title['id']))
            return total