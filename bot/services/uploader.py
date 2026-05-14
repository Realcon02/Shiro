from io import BytesIO

from discord import TextChannel, File
from aiohttp import ClientSession, ClientTimeout

from bot.services import LibAPI


class DiscordUploader:
    def __init__(self, bot, upload_channel_id: int):
        self.bot = bot
        self.channel_id = upload_channel_id
        self.session: ClientSession | None = None

        # кеш: hash(bytes) -> url
        self._cache: dict[int, str] = {}

    async def initialize(self):
        self.session = ClientSession(
            timeout=ClientTimeout(total=10, connect=5),
        )

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def _is_url_valid(self, url: str) -> bool:
        """
        Проверяет доступность CDN-ссылки HEAD-запросом.
        Возвращает False при любой сетевой ошибке или не-200 статусе.
        """
        try:
            async with self.session.head(url) as resp:
                return resp.status == 200
        except Exception:
            return False

    async def _upload_and_get_url(self, file_bytes: bytes, filename: str = "image.jpg") -> str:
        """
        Загружает файл в Discord и возвращает CDN URL.
        Использует кеш, чтобы не загружать одинаковые файлы повторно.
        Если кешированная ссылка протухла — перезаливает и обновляет кеш.
        """
        file_hash = hash(file_bytes)

        if file_hash in self._cache:
            cached_url = self._cache[file_hash]
            if await self._is_url_valid(cached_url):
                return cached_url
            del self._cache[file_hash]

        channel = self.bot.get_channel(self.channel_id)

        if not channel or not isinstance(channel, TextChannel):
            raise RuntimeError("Upload channel not found or invalid")

        file = File(BytesIO(file_bytes), filename=filename)
        msg = await channel.send(file=file)

        if not msg.attachments:
            raise RuntimeError("Discord did not return attachment URL")

        url = msg.attachments[0].url
        self._cache[file_hash] = url

        return url

    async def get_url_from_libapi(self, lib_api: LibAPI, slug_url: str, site_id: int):
        cover_path = await lib_api.get_work_cover_path(site_id, slug_url)
        cover_bytes = await lib_api.get_work_cover(site_id, cover_path)
        return await self._upload_and_get_url(cover_bytes)
