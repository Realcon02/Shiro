FROM python:3.13.12-slim AS build

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates


FROM build AS python-req

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt


FROM python-req AS base

WORKDIR /app

COPY bot bot
COPY config.py config.py
COPY main.py main.py


FROM base AS run

WORKDIR /app

ENTRYPOINT ["python", "-u", "main.py"]