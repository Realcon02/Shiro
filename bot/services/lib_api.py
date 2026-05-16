from aiohttp import ClientSession, ClientTimeout, ClientConnectorError, ServerDisconnectedError
from aiohttp_retry import RetryClient, ExponentialRetry

from bot.core import SITES, ChapterInfo, WorkSearchResult


def _get_site(site_id: int):
    site = SITES.get(site_id)

    if not site:
        raise ValueError(f"Unknown site_id: {site_id}")

    return site


def _api(api_url: str, path: str) -> str:
    """Склеивает URL_API и последующий путь"""
    return api_url.strip('/') + '/' + path.strip('/')


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
    async def search_works(self, site_id: int, searched_work: str) -> list[WorkSearchResult]:
        site = _get_site(site_id)

        url = _api(site.api_url, 'manga')
        params = {
            'q': searched_work,
            'site_id[]': site_id
        }
        headers = site.headers
        async with self.session.get(url=url, params=params, headers=headers) as resp:
            works: list = (await resp.json())['data']

            return [
                WorkSearchResult(
                    id=w['id'],
                    site_id=site_id,
                    name=w['name'],
                    rus_name=w['rus_name'] or None,
                    slug_url=w['slug_url'],
                )
                for w in works
            ]

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

    async def search_work(self, site_id: int, work_id: int, searched_work: str) -> WorkSearchResult:
        """Ищет произведение по названию и ID, возвращает информацию о нём"""

        site = _get_site(site_id)

        url = _api(site.api_url, 'manga')
        params = {
            'q': searched_work,
            'site_id[]': site_id
        }
        headers = site.headers
        async with self.session.get(url=url, params=params, headers=headers) as resp:
            works: list = (await resp.json())['data']

            work = next(
                (w for w in works if w['id'] == work_id),
                None
            )

            if work is None:
                raise IndexError(
                    f'Произведение с ID {work_id} не найдено '
                    f'среди результатов поиска "{searched_work}"'
                )

            return WorkSearchResult(
                id=work['id'],
                site_id=site_id,
                name=work['name'],
                rus_name=work['rus_name'] or None,
                slug_url=work['slug_url'],
            )

    # Функции извлечения информации
    async def get_chapter_info(self, site_id: int, slug_url_work: str, chapter_id: int) -> ChapterInfo:
        """Возвращает том, номер и название запрошенной главы, а также id ветки, в которой находится глава"""

        site = _get_site(site_id)
        headers = site.headers

        volume = ''
        number = ''
        branch_id: str | None = None

        url = _api(site.api_url, f'manga/{slug_url_work}/chapters')
        async with self.session.get(url=url, headers=headers) as resp:
            chapters: list = (await resp.json())['data']

            for chapter in chapters:
                for branch in chapter['branches']:
                    if branch['id'] == chapter_id:
                        volume = chapter['volume']
                        number = chapter['number']
                        branch_id = branch['branch_id']
                        break
                else:
                    continue
                break

        url = _api(site.api_url, f'manga/{slug_url_work}/chapter')
        params = {
            'number': number,
            'volume': volume
        }
        if branch_id:
            params['branch_id'] = branch_id

        async with self.session.get(url=url, params=params, headers=headers) as resp:
            name = (await resp.json())['data']['name']

        return ChapterInfo(
            volume=volume,
            number=number,
            name=name,
            branch_id=branch_id,
        )

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
