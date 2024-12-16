# syntax = docker/dockerfile:1.0-experimental

# Base image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim as build
RUN apt-get update && apt-get install -y build-essential curl libpq-dev

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

COPY ./requirements.txt .
RUN uv venv /opt/venv && \
    uv pip install -r requirements.txt && \
    uv pip install psycopg2 ffmpeg-python

# App image
FROM python:3.12-slim-bookworm as app-stage
COPY --from=build /opt/venv /opt/venv
RUN apt-get update && apt-get install -y libpq-dev ffmpeg
WORKDIR /app/hmtc
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:/app/hmtc"
ENV FLASK_APP="hmtc/app.py"
ENV SOLARA_APP="hmtc/pages"

CMD ["flask", "run", "--host=0.0.0.0"]

