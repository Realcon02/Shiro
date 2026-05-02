import discord
from discord import ButtonStyle
from discord.ui import DesignerView, Container, TextDisplay, ActionRow, Button, Section, Thumbnail


class ChapterNotificationView(DesignerView):
    """
    Components V2 уведомление о новой главе.
    Принимает данные главы и строит макет через DesignerView.
    """

    def __init__(self,
                 work_name,
                 volume,
                 number,
                 chapter_name,
                 thumbnail_url,
                 chapter_url):
        super().__init__(timeout=None)

        self._work_name = work_name
        self._volume = volume
        self._number = number
        self._chapter_name = chapter_name
        self._cover = thumbnail_url
        self._url = chapter_url

        self.add_item(self._build_container())

    def _build_container(self) -> Container:
        return Container(
            self._build_section(),
            self._build_actions(),
            colour=discord.Color.green(),
        )

    def _build_section(self) -> Section:
        line = f"### Том {self._volume}, Глава {self._number}"
        if self._chapter_name.strip():
            line += f" — {self._chapter_name.strip()}"

        text = TextDisplay(
            f"## Вышла новая глава!\n"
            f"{line}\n"
            f"{self._work_name}"
        )

        thumbnail = Thumbnail(url=self._cover)

        return Section(text, accessory=thumbnail)

    def _build_actions(self) -> ActionRow:
        return ActionRow(
            Button(
                label="Читать",
                url=self._url,
                style=ButtonStyle.link,
                emoji="📖",
            )
        )
