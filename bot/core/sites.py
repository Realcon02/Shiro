from dataclasses import dataclass


@dataclass(frozen=True)
class SiteConfig:
    id: int
    name: str
    base_url: str
    api_url: str
    headers: dict[str, str]
    emoji_name: str


MANGALIB = SiteConfig(
    id=1,
    name='mangalib',
    base_url='https://mangalib.me',
    api_url='https://api.cdnlibs.org/api/',
    headers={
        'Referer': 'https://mangalib.me/',
        'Site-Id': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    },
    emoji_name='mangalib_icon',
)

RANOBELIB = SiteConfig(
    id=3,
    name='ranobelib',
    base_url='https://ranobelib.me',
    api_url='https://api.cdnlibs.org/api/',
    headers={
        'Referer': 'https://ranobelib.me/',
        'Site-Id': '3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    },
    emoji_name='ranobelib_icon',
)

SITES = {
    MANGALIB.id: MANGALIB,
    RANOBELIB.id: RANOBELIB,
}
