from dataclasses import dataclass
from datetime import datetime

from discord import AppEmoji


@dataclass(frozen=True)
class WorkInfo:
    site_id: int
    name: str
    rus_name: str | None
    slug_url: str


@dataclass(frozen=True)
class ChapterInfo:
    volume: str
    number: str
    name: str | None
    branch_id: int | None


@dataclass(frozen=True)
class WorkSearchResult:
    id: int
    site_id: int
    name: str
    rus_name: str | None
    slug_url: str


@dataclass(frozen=True)
class SubRecord:
    id: int
    type: str
    channel_id: int
    site_id: int | None
    slug_url: str
    description: str


@dataclass(frozen=True)
class SubListItem:
    title: str
    url: str
    sub_type: str
    channel_id: int
    site_icon: AppEmoji | None


@dataclass(frozen=True)
class Subscription:
    id: int
    target_type: str
    target_id: int
    newest_id_chapter: int
    created_at: datetime


@dataclass(frozen=True)
class GuildSub:
    guild_id: int
    channel_id: int
