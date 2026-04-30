import discord
from discord import ButtonStyle
from discord.ui import DesignerView, Container, TextDisplay, ActionRow, Button, Section, Thumbnail


SITE_URLS = {
    1: "https://mangalib.me",
    3: "https://ranobelib.me"
}


class ChapterNotificationView(DesignerView):
    """
    Components V2 уведомление о новой главе.
    Принимает данные главы и строит макет через DesignerView.
    """

    def __init__(self, work_info, chapter_info, thumbnail_url):
        super().__init__(timeout=None)
        self._work = work_info
        self._chapter = chapter_info
        self._cover = thumbnail_url

        self.add_item(self._build_container())

    def _build_container(self) -> Container:
        return Container(
            self._build_section(),
            self._build_actions(),
            colour=discord.Color.green(),
        )

    def _build_section(self) -> Section:
        text = TextDisplay(
            f"## Вышла новая глава!\n"
            f"### Том {self._chapter['volume']}, глава {self._chapter['number']} — «{self._chapter['name']}»\n"
            f"{self._work['rus_name'] or self._work['name']}"
        )

        thumbnail = Thumbnail(url=self._cover)

        return Section(text, accessory=thumbnail)

    def _build_url(self):
        url = f"https://ranobelib.me/ru/{self._work['slug_url']}/read/v{self._chapter['volume']}/c{self._chapter['number']}"
        if bid := self._chapter['branch_id']:
            url += f'?bid={bid}'

        return url

    def _build_chapter_url(self):
        base = SITE_URLS.get(self._work['site_id'])

        if not base:
            raise ValueError(f"Unknown site_id: {self._work['site_id']}")

        url = f"{base}/ru/{self._work['slug_url']}/read/v{self._chapter['volume']}/c{self._chapter['number']}"

        if self._chapter.get("branch_id"):
            url += f"?bid={self._chapter['branch_id']}"

        return url

    def _build_actions(self) -> ActionRow:
        return ActionRow(
            Button(
                label="Читать",
                url=self._build_url(),
                style=ButtonStyle.link,
                emoji="📖",
            )
        )
