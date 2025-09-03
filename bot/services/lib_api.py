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

    async def search_work(self, site_id: int, searched_work: str) -> list[OptionChoice]:
        url = 'manga'
        params = {'q': searched_work, 'site_id[]': site_id}

        async with self.session.get(url=url, params=params) as resp:
            works: list = (await resp.json())['data']

            total = []
            for work in works:
                name_work = work['rus_name'] or work['name']
                total.append(name_work if len(name_work) <= 100 else name_work[:97] + '...')
            return total

    async def search_id_and_slug_url_work(self, site_id: int, searched_work: str) -> tuple[int, str]:
        url = 'manga'
        params = {'q': searched_work, 'site_id[]': site_id}

        async with self.session.get(url=url, params=params) as resp:
            works: list = (await resp.json())['data']

            if len(works) > 1:
                print(f'search_id_and_slug_url_work: Найдено несколько произведений по запросу \'{searched_work}\'')
            return works[0]['id'], works[0]['slug_url']

    async def search_newest_id_chapter_work(self, slug_url_title: str):
        url = f'manga/{slug_url_title}/chapters'

        async with self.session.get(url=url) as resp:
            chapters: list = (await resp.json())['data']

            searched_id = 0
            for chapter in chapters:
                for branch in chapter['branches']:
                    searched_id = max(searched_id, branch['id'])
            return searched_id
