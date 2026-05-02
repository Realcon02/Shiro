FROM python:3.13.12-slim AS build

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates

# Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv


FROM build AS python-req

WORKDIR /app

COPY pyproject.toml uv.lock ./

# --frozen — не обновлять lockfile, использовать как есть
# --no-dev — не ставить dev-зависимости
RUN uv sync --frozen --no-dev


FROM build AS base

WORKDIR /app

# Копируем готовое окружение из предыдущего этапа
COPY --from=python-req /app/.venv .venv

COPY bot bot
COPY config.py config.py
COPY main.py main.py


FROM base AS run

WORKDIR /app

# Запускаем через uv, чтобы он сам подхватил .venv
ENTRYPOINT ["uv", "run", "--frozen", "python", "-u", "main.py"]