from dataclasses import dataclass


@dataclass(frozen=True)
class SubTypeConfig:
    id: str
    name: str
    emoji: str


WORKS = SubTypeConfig(
    id='works',
    name='Произведение',
    emoji='📖'
)

TEAMS = SubTypeConfig(
    id='teams',
    name='Команда',
    emoji='👥'
)

BRANCHES_WORKS = SubTypeConfig(
    id='branches_works',
    name='Ветка произведения',
    emoji='🌿'
)

WORKS_TEAMS = SubTypeConfig(
    id='works_teams',
    name='Произведение от команды',
    emoji='📚'
)

SUB_TYPES = {
    WORKS.id: WORKS,
    TEAMS.id: TEAMS,
    BRANCHES_WORKS.id: BRANCHES_WORKS,
    WORKS_TEAMS.id: WORKS_TEAMS,
}