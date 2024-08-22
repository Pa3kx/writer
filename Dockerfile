FROM python:3.12-slim-bullseye
COPY --from=ghcr.io/astral-sh/uv:0.3.0 /uv /bin/uv
ENV PYTHONUNBUFFERED=1

RUN apt-get update

ADD . /app
WORKDIR /app

RUN uv sync

CMD ["uv", "run", "my_app", "temperature", "battery_capacity"]