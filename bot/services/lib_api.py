from aiohttp import ClientSession, ClientTimeout, ClientConnectorError, ServerDisconnectedError
from aiohttp_retry import RetryClient, ExponentialRetry

from bot.core import SITES
from bot.utils.formatters import truncate


def _get_site(site_id: int):
    site = SITES.get(site_id)

    if not site:
        raise ValueError(f"Unknown site_id: {site_id}")

    return site


def _api(api_url: str, path: str) -> str:
    """Склеивает URL_API и последующий путь"""
    return api_url + path


class LibAPI:
    """Асинхронный клиент для работы с API RanobeLIB и MangaLIB"""

    def __init__(self):
        self.session: RetryClient | None = None

    async def initialize(self):
        """Инициализация сессии"""
        # Настройка повторных попыток
        retry_options = ExponentialRetry(
            attempts=5,         # 1 попытка + 4 повтора
            start_timeout=0.1,  # Пауза перед первым повтором
            max_timeout=5.0,    # Максимальная пауза
            exceptions={        # Ошибки, при которых делаем retry
                ConnectionResetError,
                ClientConnectorError,
                ServerDisconnectedError,
                OSError,
            },
        )

        # Создаем RetryClient поверх обычной сессии
        self.session = RetryClient(
            client_session=ClientSession(
                timeout=ClientTimeout(total=30, connect=10, sock_read=15),
            ),
            retry_options=retry_options
        )
        print('[INFO] Session initialized')

    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None
            print('[INFO] Session closed')

    # Функции поиска
    async def search_works(self, site_id: int, searched_work: str) -> list[str]:
        site = _get_site(site_id)

        url = _api(site.api_url, site.api_url)
        params = {
            'q': searched_work,
            'site_id[]': site_id
        }
        headers = site.headers
        async with self.session.get(url=url, params=params, headers=headers) as resp:
            works: list = (await resp.json())['data']

            total = []
            for work in works:
                name_work: str = work['rus_name'] or work['name']
                total.append(truncate(name_work))

        return works

    async def search_newest_id_chapter_work(self, site_id: int, slug_url_work: str):
        site = _get_site(site_id)

        url = _api(site.api_url, f'manga/{slug_url_work}/chapters')
        headers = site.headers
        async with self.session.get(url=url, headers=headers) as resp:
            chapters: list = (await resp.json())['data']

            searched_id = 0
            for chapter in chapters:
                for branch in chapter['branches']:
                    searched_id = max(searched_id, branch['id'])

        return searched_id

    async def search_work(self, site_id: int, searched_work: str) -> dict:
        """Ищет произведение по названию и возвращает информацию о нём"""

        site = _get_site(site_id)

        url = _api(site.api_url, 'manga')
        params = {
            'q': searched_work,
            'site_id[]': site_id
        }
        headers = site.headers
        async with self.session.get(url=url, params=params, headers=headers) as resp:
            works: list = (await resp.json())['data']

            work = works[0]
            if len(works) > 1:
                print(f'get_work_info: Найдено несколько произведений по запросу \'{searched_work}\'\n'
                      f'Выбрано 1-е найденное произведение: \'{work}\'')

            work_info = {
                'id': work['id'],
                'site_id': site_id,
                'name': work['name'],
                'rus_name': work['rus_name'] or None,
                'slug_url': work['slug_url']
            }

        return work_info

    # Функции извлечения информации
    async def get_chapter_info(self, site_id: int, slug_url_work: str, chapter_id: int) -> dict:
        """Возвращает том, номер и название запрошенной главы, а также id ветки, в которой находится глава"""

        chapter_info = {
            'volume': '',
            'number': '',
            'name': ''
        }
        branch_id: str | None = None
        site = _get_site(site_id)
        headers = site.headers

        url = _api(site.api_url, f'manga/{slug_url_work}/chapters')
        async with self.session.get(url=url, headers=headers) as resp:
            chapters: list = (await resp.json())['data']

            for chapter in chapters:
                for branch in chapter['branches']:
                    if branch['id'] == chapter_id:
                        chapter_info['volume'] = chapter['volume']
                        chapter_info['number'] = chapter['number']
                        branch_id = branch['branch_id']
                        break
                else: continue
                break

        url = _api(site.api_url, f'manga/{slug_url_work}/chapter')
        params = {
            'number': chapter_info['number'],
            'volume': chapter_info['volume']
        }
        if branch_id != 'null': params['branch_id'] = branch_id

        async with self.session.get(url=url, params=params, headers=headers) as resp:
            name = (await resp.json())['data']['name']
            chapter_info['name'] = name

        return chapter_info

    async def get_new_chapter_ids_work(self, site_id: int, slug_url_work: str, old_chapter_id: int) -> list[int]:
        """Возвращает IDs глав для подписки типа «Тайтл»"""

        site = _get_site(site_id)

        new_ids: list[int] = []

        url = _api(site.api_url, f'manga/{slug_url_work}/chapters')
        headers = site.headers
        async with self.session.get(url=url, headers=headers) as resp:
            chapters: list = (await resp.json())['data']

            for chapter in chapters:
                for branch in chapter['branches']:
                    if (chapter_id := branch['id']) > old_chapter_id:
                        new_ids.append(chapter_id)

        return new_ids

    async def get_work_cover_path(self, site_id: int, slug_url_work: str) -> str:
        """Возвращает ссылку на обложку произведения"""

        site = _get_site(site_id)

        url = _api(site.api_url, f'manga/{slug_url_work}')
        headers = site.headers
        async with self.session.get(url=url, headers=headers) as resp:
            return (await resp.json())['data']['cover']['default']

    async def get_work_cover(self, site_id: int, cover_url: str) -> bytes | None:
        """Возвращает изображение в виде byte-кода"""

        headers = _get_site(site_id).headers
        async with self.session.get(url=cover_url, headers=headers) as resp:
            if resp.status != 200:
                raise Exception(f"Ошибка загрузки изображения: {resp.status}")
            return await resp.read()
