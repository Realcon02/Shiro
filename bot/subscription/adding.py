import discord
from discord.ext import commands
from discord import AutocompleteContext

from ..subscription.parser import search_title, search_teams_of_title, search_branches_of_title


# AutoComplete
async def get_titles_auto(ctx: AutocompleteContext):
    site = ctx.options['site']
    title = ctx.value
    return search_title(site, title)


async def get_team_or_branch_auto(ctx: AutocompleteContext):
    type_sub = ctx.options['type_sub']
    slug_url_title = ctx.options['title']

    if type_sub == 'Team':
        return search_teams_of_title(slug_url_title)
    else:  # Branch
        return search_branches_of_title(slug_url_title)


def sub_add_team(last_chapter_id: int):
    print(last_chapter_id)