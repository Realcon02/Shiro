def truncate(text: str, limit: int = 100) -> str:
    return text.strip() if len(text) <= limit else text[:limit - 3].strip() + '...'