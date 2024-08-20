from typing import List

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
    data = requests.get(
        f"https://api.lib.social/api/manga?fields[]=rate_avg&fields[]=rate&fields[]=releaseDate&q={quote(title_name)}&site_id[]={site_id}"
    ).json()['data']
    print(len(data))
    total = []
    for title in data:
        total.append(OptionChoice(title['rus_name'] or title['name'], title['id']))
    print(total)
    return total


def search_team(team_name: str) -> dict:
    data = requests.get(f"https://api.lib.social/api/teams?q={quote(team_name)}").json()['data'][0]
    if data:
        id = data['id']
        name = data['name']
        avatar_url = f'https://ranobelib.me{data['cover']['default']}'
        output = {
            "id": id,
            "name": name,
            "avatar_url": avatar_url
        }
        return output
    return {}


def search_title_by_team(team_id: int, title_name: str) -> dict:
    search_title = requests.get(
        f"https://api.lib.social/api/manga?fields[]=rate_avg&fields[]=rate&fields[]=releaseDate&q={quote(title_name)}&site_id[]=3"
    ).json()['data'][0]
    titles = requests.get(
        f"https://api.lib.social/api/manga?fields[]=rate&fields[]=rate_avg&fields[]=userBookmark&site_id[]=3&target_id={team_id}&target_model=team").json()[
        'data']
    for title in titles:
        if title['id'] == search_title['id']:
            id = title['id']
            name = title['rus_name']
            avatar_url = f'https://ranobelib.me{title['cover']['default']}'
            output = {
                "id": id,
                "name": name,
                "avatar_url": avatar_url
            }
            return output
    return {}


def create_subscription(team_id: int, title_id: int):
    chapters = requests.get(f"https://api.lib.social/api/teams/{team_id}/chapters?page=1").json()['data']
    for chp in chapters:
        if chp:
            pass


def publish_chapters(team_id: int, title_id: int, last_chapter_id: int):
    chapters = requests.get(f"https://api.lib.social/api/teams/{team_id}/chapters?page=1").json()['data']

    if chapters[0]['id'] != last_chapter_id:
        pass
    return {}


def parsing():
    pass
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as file:
            file.write(response_json["data"][0]["chapter"]["id"])
        return
    else:
        with open('data.json', 'r') as file:
            pr_id = file.read()
        if pr_id == response_json["data"][0]["chapter"]["id"]:
            return

    new_chps = []
    for i in response_json['data']:
        chp = i["chapter"]
        if chp["id"] == pr_id:
            return new_chps

        volume = chp['volume']
        number = chp['number']
        title = chp['name']
        added = chp['created_at']
        manga_id = chp['manga_id']

        new_chps.append(Chapter(
            volume,
            number,
            title,
            added,
            manga_id
        ))


def parser(team_name: str, title_name: str):
    pass
