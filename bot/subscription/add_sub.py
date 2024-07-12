import discord
from config import embed_color

from dotenv import load_dotenv
import os

bot = discord.Bot()


class TypeSubscriptionView(discord.ui.View):
    def __init__(self, author_id: int, *items):
        super().__init__(*items)
        self.author_id = author_id

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
    # @discord.ui.button(label="Click me!", style=discord.ButtonStyle.primary, emoji="😎")
    async def select_callback(self, select: discord.ui.Select,
                              interaction: discord.Interaction):  # the function called when the user is done selecting options
        if interaction.user.id == self.author_id:
            if select.values[0] == 'team':
                await interaction.response.send_modal(InputTeamModal())
            elif select.values[0] == 'branch':
                await interaction.response.send_message('В разработке')


class InputTeamModal(discord.ui.Modal):
    def __init__(self, *args, title: str = 'Сбор данных'):
        super().__init__(*args, title=title)

        self.add_item(discord.ui.InputText(label="Введите название команды"))
        self.add_item(discord.ui.InputText(label="Введите название тайтла"))

    async def callback(self, interaction: discord.Interaction):
        pass
        # await interaction.respond(f'{self.children[0].value}\n{self.children[1].value}')

    # embed = discord.Embed(title="Modal Results")
    # embed.add_field(name="Short Input 2", value=self.children[0].value)
    # await interaction.response.send_message(embeds=[embed])


class InputBranchModal(discord.ui.Modal):
    def __init__(self, *args, title: str = 'Сбор данных'):
        super().__init__(*args, title=title)

        self.add_item(discord.ui.InputText(label="Введите название тайтла"))
        self.add_item(discord.ui.InputText(label="Введите название ветки"))

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
        view=TypeSubscriptionView(author_id=ctx.author.id),
        ephemeral=False  # Сменить на True
    )


load_dotenv()
bot.run(os.getenv('TOKEN'))
