import discord
from discord import Interaction

from config import embed_color, timeout_command

from dotenv import load_dotenv
import os

bot = discord.Bot()


class TypeSubscriptionView(discord.ui.View):
    def __init__(self, author_id: int, timeout: int):
        super().__init__(timeout=timeout)
        self.author_id = author_id

        self.team_embed = discord.Embed(
            title='Выбрана «Команда»',
            description='Вы можете получать уведомления о определённых тайтлах или обо всех сразу. Нажмите на соответсвующую кнопку.',
            color=embed_color
        )

        self.branch_embed = discord.Embed(
            title='Выбрана «Ветка»',
            description='Введите номер ветки, начиная счёт от 1.',
            color=embed_color
        )

    async def on_timeout(self):
        self.disable_all_items()

    @discord.ui.select(
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Команда",
                value='team'
            ),
            discord.SelectOption(
                label="Ветка",
                value='branch'
            )
        ]
    )
    async def select_callback(self, select: discord.ui.Select,
                              interaction: discord.Interaction):
        if interaction.user.id == self.author_id:
            select.disabled = True
            await interaction.edit(view=self)
            # mes = await interaction.
            # await mes.edit(view=self)
            if select.values[0] == 'team':
                # await interaction.response.send_modal(InputTeamModal())
                # await interaction.followup.send(embed=self.team_embed, view=ButtonTeamView())
                await interaction.respond(embed=self.team_embed, view=ButtonTeamView(timeout=timeout_command))
            elif select.values[0] == 'branch':
                await interaction.followup.send('In developing')  # Заглушка
                # await interaction.respond(embed=self.branch_embed, view=ButtonTeamView(timeout=timeout_command))


class ButtonTeamView(discord.ui.View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)
        self.flag = True

    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(view=self)

    @discord.ui.button(label='Один тайтл', style=discord.ButtonStyle.primary)
    async def one_title_button(self, button: discord.Button, interaction: discord.Interaction):
        # self.disable_all_items()
        # await interaction.response.edit_message(view=self)
        # await interaction.respond('Response to... Один тайтл')
        if self.flag:
            self.flag = False
            await interaction.response.send_modal(InputTeamModal())
        else:
            self.disable_all_items()
            await interaction.response.edit_message(view=self)
            await interaction.respond('Вы уже вводили данные')

    @discord.ui.button(label='Все тайтлы', style=discord.ButtonStyle.primary, disabled=True)
    async def all_titles_button(self, button: discord.Button, interaction: discord.Interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        await interaction.respond('Response to... Все тайтлы... В планах')


class ButtonBranchView(discord.ui.View):
    async def on_timeout(self):
        self.disable_all_items()
        await self.message.edit(view=self)

    @discord.ui.button(label='Ввести данные', style=discord.ButtonStyle.premium)
    async def button(self, button: discord.Button, interaction: discord.Interaction):
        self.disable_all_items()
        await interaction.response.edit_message(view=self)
        await interaction.respond('Response to... Ветка')


class InputTeamModal(discord.ui.Modal):
    def __init__(self, *args, title: str = 'Сбор данных'):
        super().__init__(*args, title=title)

        self.add_item(discord.ui.InputText(label="Введите название команды", max_length=128))
        self.add_item(discord.ui.InputText(label="Введите название тайтла", max_length=128))

    async def callback(self, interaction: discord.Interaction):
        await interaction.respond(f'{self.children[0].value}\n{self.children[1].value}')

    # embed = discord.Embed(title="Modal Results")
    # embed.add_field(name="Short Input 2", value=self.children[0].value)
    # await interaction.response.send_message(embeds=[embed])


class InputBranchModal(discord.ui.Modal):
    def __init__(self, *args, title: str = 'Сбор данных'):
        super().__init__(*args, title=title)

        self.add_item(discord.ui.InputText(label="Введите название тайтла", max_length=128))
        self.add_item(discord.ui.InputText(label="Введите название ветки", max_length=128))

    async def callback(self, interaction: discord.Interaction):
        pass


@bot.command()
async def flavor(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="Создание подписки",
        description="Для начала выберите тип подписки:",
        color=embed_color
    )
    embed.add_field(
        name="Команда",
        value="Получение уведомлений о новых главах тайтла от определённой команды",
        inline=True
    )
    embed.add_field(
        name="Ветка",
        value="Получение уведомлений о новых главах тайтла из определённой ветки",
        inline=True
    )
    embed.add_field(
        name="Примечание",
        value="При выборе типа «Ветка», если на сайте есть только одна ветка, введите `1`",
        inline=False
    )

    await ctx.respond(
        embed=embed,
        view=TypeSubscriptionView(author_id=ctx.author.id, timeout=timeout_command),
        ephemeral=False  # Сменить на True
    )


load_dotenv()
bot.run(os.getenv('TOKEN'))
