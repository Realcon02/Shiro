import requests
from urllib.parse import quote
import os

from discord import OptionChoice

BASE_URL = 'https://api.cdnlibs.org/api'

class Chapter:
    def __init__(self, volume, number, title, added, manga_id):
        self.volume = volume
        self.number = number
        self.title = title
        self.added = added
        self.manga_id = manga_id


def search_title(site_id: int, title_name: str) -> list[OptionChoice]:
    titles = requests.get(
        f"{BASE_URL}/manga?fields[]=rate_avg&fields[]=rate&fields[]=releaseDate&q={quote(title_name)}&site_id[]={site_id}"
    ).json()['data']
    total = []
    for title in titles:
        name_title = title['rus_name'] or title['name']
        total.append(OptionChoice(name_title if len(name_title) <= 100 else name_title[:97]+'...', title['id']))
    return total


def search_teams_of_title(slug_url_title: str) -> list[OptionChoice]:
    teams = requests.get(f"{BASE_URL}/manga/{slug_url_title}?fields[]=teams").json()['data']['teams']
    total = []
    for team in teams:
        total.append(OptionChoice(team['name'], team['id']))
    return total


def search_branches_of_title(slug_url_title: str) -> list[OptionChoice]:
    id_title = slug_url_title.split('--', 1)[0]
    branches = requests.get(f"{BASE_URL}/branches/{id_title}").json()['data']
    total = []
    if not branches:
        return [OptionChoice('Нет веток', -1)]
    for branch in branches:
        total.append(OptionChoice(branch['teams'][0]['name'], branch['id']))
    return total


def search_newest_id_chapter_work(slug_url_title: str, newest_id_chapter: int):
    chapters: list = requests.get(f"{BASE_URL}/manga/{slug_url_title}/chapters").json()['data']
    searched_id = False
    for chapter in chapters:
        for branch in chapter['branches']:
            if branch['id'] > searched_id:
                searched_id = branch['id']
    return searched_id


def search_newest_id_chapter_branch_work(slug_url_title: str, branch_id: str, newest_id_chapter: int):
    chapters: list = requests.get(f"{BASE_URL}/manga/{slug_url_title}/chapters").json()['data']
    searched_id = False
    for chapter in chapters:
        for branch in chapter['branches']:
            if branch['branch_id'] == branch_id and branch['id'] > searched_id:
                searched_id = branch['id']
    return searched_id


def search_newest_id_chapter_team(slug_url_team: str, newest_id_chapter: int):
    id = requests.get(f"{BASE_URL}/teams/{slug_url_team}/chapters?page=1").json()['data'][0]['chapter']['id']
    if id > newest_id_chapter:
        return id
    return False


def search_newest_id_chapter_work_team(slug_url_team: str, newest_id_chapter: int, work_id: int):
    chapters: list = requests.get(f"{BASE_URL}/teams/{slug_url_team}/chapters?page=1").json()['data']
    for chapter in chapters:
        if chapter['manga']['id'] == work_id:
            if chapter['chapter']['id'] > newest_id_chapter:
                return chapter['chapter']['id']
            break
    return False


def publish_chapters(team_id: int, title_id: int, last_chapter_id: int):
    chapters = requests.get(f"{BASE_URL}/teams/{team_id}/chapters?page=1").json()['data']

    if chapters[0]['id'] != last_chapter_id:
        pass
    return {}
