from io import BytesIO

import discord

from bot.services import LibAPI


class DiscordUploader:
    def __init__(self, bot, upload_channel_id: int):
        self.bot = bot
        self.channel_id = upload_channel_id

        # кеш: hash(bytes) -> url
        self._cache: dict[int, str] = {}

    async def _upload_and_get_url(self, file_bytes: bytes, filename: str = "image.jpg") -> str:
        """
        Загружает файл в Discord и возвращает CDN URL.
        Использует кеш, чтобы не загружать одинаковые файлы повторно.
        """

        file_hash = hash(file_bytes)

        if file_hash in self._cache:
            return self._cache[file_hash]

        channel = self.bot.get_channel(self.channel_id)

        if not channel or not isinstance(channel, discord.TextChannel):
            raise RuntimeError("Upload channel not found or invalid")

        file = discord.File(BytesIO(file_bytes), filename=filename)

        msg = await channel.send(file=file)

        if not msg.attachments:
            raise RuntimeError("Discord did not return attachment URL")

        url = msg.attachments[0].url

        # сохраняем в кеш
        self._cache[file_hash] = url

        return url

    async def get_url_from_libapi(self, lib_api: LibAPI, slug_url: str, site_id: int):
        cover_path = await lib_api.get_work_cover_path(site_id, slug_url)
        cover_bytes = await lib_api.get_work_cover(site_id, cover_path)
        return await self._upload_and_get_url(cover_bytes)
