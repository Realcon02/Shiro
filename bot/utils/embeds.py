import math

import discord

from config import embed_color


TYPE_LABELS: dict[str, str] = {
    'works':         ':book:',
    'teams':         ':busts_in_silhouette:',
    'branches_works':':herb:',
    'works_teams':   ':books:',
}
'''
'works':          '📖 Произведение',
'teams':          '👥 Команда',
'branches_works': '🌿 Ветка произведения',
'works_teams':    '📚 Произведение от команды',
'''

ITEMS_PER_PAGE = 10


def build_sub_pages(
    records: list,
    guild_name: str,
) -> list[discord.Embed]:
    """Разбивает список подписок на страницы-эмбеды."""
    if not records:
        embed = discord.Embed(
            title=f'Подписки сервера «{guild_name}»',
            description='На этом сервере пока нет ни одной подписки.',
            color=embed_color,
        )
        return [embed]

    total_pages = math.ceil(len(records) / ITEMS_PER_PAGE)
    pages: list[discord.Embed] = []

    for page_idx in range(total_pages):
        chunk = records[page_idx * ITEMS_PER_PAGE : (page_idx + 1) * ITEMS_PER_PAGE]

        embed = discord.Embed(
            title=f'Подписки сервера «{guild_name}»',
            description='-# :book:⠀Произведение\n' + \
                        '-# :busts_in_silhouette:⠀Команда\n' + \
                        '-# :herb:⠀Ветка произведения\n' + \
                        '-# :books:⠀Произведение от команды',
            color=embed_color,  # discord.Color.blurple()
        )
        embed.set_footer(text=f'Страница {page_idx + 1}/{total_pages} ・ Всего подписок: {len(records)}')

        for i, row in enumerate(chunk):
            col_type = TYPE_LABELS.get(str(row['type']), str(row['type']))
            col_desc = row['description'] or '—'
            col_chan = f'<#{row["channel_id"]}>'

            embed.add_field(name='Тип' if i == 0 else '',      value=col_type, inline=True)
            embed.add_field(name='Наименование' if i == 0 else '', value=col_desc, inline=True)
            embed.add_field(name='Канал' if i == 0 else '',    value=col_chan, inline=True)

        pages.append(embed)

    return pages