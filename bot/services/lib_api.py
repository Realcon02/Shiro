import aiohttp
from aiohttp import ClientSession


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


    # Функции поиска
    async def search_works(self, site_id: int, searched_work: str) -> list[str]:
        url = 'manga'
        params = {
            'q': searched_work,
            'site_id[]': site_id
        }
        async with self.session.get(url=url, params=params) as resp:
            works: list = (await resp.json())['data']

            total = []
            for work in works:
                name_work: str = work['rus_name'] or work['name']
                total.append(name_work if len(name_work) <= 100 else name_work[:97].strip() + '...')

        return total

    async def search_newest_id_chapter_work(self, slug_url_work: str):
        url = f'manga/{slug_url_work}/chapters'

        async with self.session.get(url=url) as resp:
            chapters: list = (await resp.json())['data']

            searched_id = 0
            for chapter in chapters:
                for branch in chapter['branches']:
                    searched_id = max(searched_id, branch['id'])

        return searched_id

    async def search_work(self, site_id: int, searched_work: str) -> dict:
        """Ищет произведение по названию и возвращает информацию о нём"""

        url = 'manga'
        params = {
            'q': searched_work,
            'site_id[]': site_id
        }
        async with self.session.get(url=url, params=params) as resp:
            works: list = (await resp.json())['data']

            work = works[0]
            if len(works) > 1:
                print(f'get_work_info: Найдено несколько произведений по запросу \'{searched_work}\'\n'
                      f'Выбрано 1-е найденное произведение: \'{work}\'')

            work_info = {
                'id': work['id'],
                'name': work['name'],
                'rus_name': work['rus_name'] or None,
                'slug_url': work['slug_url']
            }

        return work_info


    # Функции извлечения информации
    async def get_chapter_info(self, slug_url_work, chapter_id) -> dict:
        """Возвращает том, номер и название запрошенной главы"""

        chapter_info = {
            'volume': '',
            'number': '',
            'name'  : ''
        }
        branch_id: int

        url = f'manga/{slug_url_work}/chapters'
        async with self.session.get(url=url) as resp:
            chapters: list = (await resp.json())['data']

            for chapter in chapters:
                for branch in chapter['branches']:
                    if branch['id'] == chapter_id:
                        chapter_info['volume'] = chapter['volume']
                        chapter_info['number'] = chapter['number']
                        branch_id = branch['branch_id']

        url = f'manga/{slug_url_work}/chapter'
        params = {
            'branch_id': branch_id,
            'number': chapter_info['number'],
            'volume': chapter_info['volume']
        }
        async with self.session.get(url=url, params=params) as resp:
            name = (await resp.json())['data']['name']
            chapter_info['name'] = name

        return chapter_info

    async def get_new_chapter_ids_work(self, slug_url_work, old_chapter_id) -> list[int]:
        """Возвращает IDs глав для подписки типа «Тайтл»"""

        new_ids: list[int] = []

        url = f'manga/{slug_url_work}/chapters'
        async with self.session.get(url=url) as resp:
            chapters: list = (await resp.json())['data']

            for chapter in chapters:
                for branch in chapter['branches']:
                    if (chapter_id:=branch['id']) > old_chapter_id:
                        new_ids.append(chapter_id)

        return new_ids
