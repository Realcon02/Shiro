import discord
from discord import ButtonStyle
from discord.ui import DesignerView, Container, TextDisplay, ActionRow, Button, Section, Separator


class SubItem:
    def __init__(self, item):
        self._title = item['title']
        self._url = item['url']
        self._sub_type = item['sub_type']
        self._channel_id = item['channel_id']
        self._icon = item['site_icon']

    def build(self) -> Section:
        text = TextDisplay(
            f"{self._title}\n"
            f"-# {self._sub_type} ・ <#{self._channel_id}>"
        )

        button = Button(
            label="Перейти",
            url=self._url,
            style=ButtonStyle.link,
            emoji=self._icon or "📖",
        )

        return Section(text, accessory=button)


class SubListView(DesignerView):
    def __init__(self, subs, guild_name: str, author: discord.User | discord.Member):
        super().__init__(timeout=180.0)
        self._subs = subs
        self._guild_name = guild_name
        self._author = author

        self._page = 0
        self._per_page = 7
        self._total_pages = (len(subs) - 1) // self._per_page + 1

        self.add_item(self._build_container())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self._author.id:
            await interaction.response.send_message(
                "Это меню открыто не для вас.", ephemeral=True
            )
            return False
        return True

    def _build_container(self) -> Container:
        if not self._subs:
            return Container(
                self._build_header(),
                Separator(),
                TextDisplay(
                    "На этом сервере пока нет ни одной подписки."
                )
            )

        return Container(
            self._build_header(),
            Separator(),
            *self._build_items(),
            Separator(),
            self._build_actions(),
        )

    def _build_header(self) -> TextDisplay:
        return TextDisplay(
            f"# Подписки сервера «{self._guild_name}»\n"
            f"> Всего подписок: {len(self._subs)}"
        )

    def _build_items(self):
        components = []

        subs = self._get_page_subs()
        for i, item in enumerate(subs):
            components.append(SubItem(item).build())
            if i < len(subs) - 1:
                components.append(Separator())

        return components

    def _build_actions(self):
        first_btn = Button(label='<<', disabled=self._is_first_page())
        prev_btn  = Button(label='<',  disabled=self._is_first_page())
        page_btn  = Button(label=f'{self._page + 1}/{self._total_pages}', disabled=True)
        next_btn  = Button(label='>',  disabled=self._is_last_page())
        last_btn  = Button(label='>>', disabled=self._is_last_page())

        first_btn.callback = self._first_page
        prev_btn.callback  = self._prev_page
        next_btn.callback  = self._next_page
        last_btn.callback  = self._last_page

        return ActionRow(first_btn, prev_btn, page_btn, next_btn, last_btn)

    async def _first_page(self, interaction: discord.Interaction):
        self._page = 0
        await self._update(interaction)

    async def _next_page(self, interaction: discord.Interaction):
        self._page += 1
        await self._update(interaction)

    async def _prev_page(self, interaction: discord.Interaction):
        self._page -= 1
        await self._update(interaction)

    async def _last_page(self, interaction: discord.Interaction):
        self._page = self._total_pages - 1
        await self._update(interaction)

    async def _update(self, interaction):
        self._page = max(0, min(self._page, self._total_pages - 1))

        self.clear_items()
        self.add_item(self._build_container())

        await interaction.response.edit_message(view=self)

    def _get_page_subs(self):
        start = self._page * self._per_page
        end = start + self._per_page
        return self._subs[start:end]

    def _is_first_page(self):
        return self._page == 0

    def _is_last_page(self):
        return self._page == self._total_pages - 1
