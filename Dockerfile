# syntax = docker/dockerfile:1.0-experimental

# Base image
FROM python:3.12 as build

RUN apt-get update && apt-get install -y build-essential curl libpq-dev
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod -R 655 /install.sh && /install.sh && rm /install.sh
COPY ./requirements.txt .
RUN /root/.cargo/bin/uv venv /opt/venv && \
    /root/.cargo/bin/uv pip install --no-cache -r requirements.txt && \
    /root/.cargo/bin/uv pip install --no-cache psycopg2
# App image
FROM python:3.12-slim-bookworm as app-stage
COPY --from=build /opt/venv /opt/venv
RUN apt-get update && apt-get install -y libpq-dev ffmpeg yt-dlp

WORKDIR /app
COPY . .
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/hmtc"
ENV FLASK_APP="hmtc/app.py"
ENV SOLARA_APP="hmtc/pages"
CMD ["flask", "run","--host=0.0.0.0"]
# CMD ["solara", "run", "hmtc/pages", "--host=0.0.0.0", "--port=8765"]
