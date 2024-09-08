import requests
from urllib.parse import quote
import os

from discord import OptionChoice


class Chapter:
    def __init__(self, volume, number, title, added, manga_id):
        self.volume = volume
        self.number = number
        self.title = title
        self.added = added
        self.manga_id = manga_id


def search_title(site_id: int, title_name: str) -> list[OptionChoice]:
    titles = requests.get(
        f"https://api.lib.social/api/manga?fields[]=rate_avg&fields[]=rate&fields[]=releaseDate&q={quote(title_name)}&site_id[]={site_id}"
    ).json()['data']
    total = []
    for title in titles:
        total.append(OptionChoice(title['rus_name'] or title['name'], title['slug_url']))
    return total


def search_teams_of_title(slug_url_title: str) -> list[OptionChoice]:
    teams = requests.get(f"https://api.lib.social/api/manga/{slug_url_title}?fields[]=teams").json()['data']['teams']
    total = []
    for team in teams:
        total.append(OptionChoice(team['name'], team['id']))
    return total


def search_branches_of_title(slug_url_title: str) -> list[OptionChoice]:
    id_title = slug_url_title.split('--', 1)[0]
    branches = requests.get(f"https://api.lib.social/api/branches/{id_title}").json()['data']
    total = []
    if not branches:
        return [OptionChoice('Нет веток', -1)]
    for branch in branches:
        total.append(OptionChoice(branch['teams'][0]['name'], branch['id']))
    return total


def search_last_chapter(slug_url_title: str, team_id: int):
    chapters: list = requests.get(f"https://api.lib.social/api/manga/{slug_url_title}/chapters").json()['data']
    chapters.reverse()
    for chapter in chapters:
        for branch in chapter['branches']:
            for team in branch['teams']:
                if team['id'] == team_id:
                    return chapter['id']


def publish_chapters(team_id: int, title_id: int, last_chapter_id: int):
    chapters = requests.get(f"https://api.lib.social/api/teams/{team_id}/chapters?page=1").json()['data']

    if chapters[0]['id'] != last_chapter_id:
        pass
    return {}
