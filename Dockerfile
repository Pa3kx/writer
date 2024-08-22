FROM python:3.12-slim-bullseye
COPY --from=ghcr.io/astral-sh/uv:0.3.0 /uv /bin/uv
ENV PYTHONUNBUFFERED=1

RUN apt-get update

# Copy the project into the image
ADD . /app
WORKDIR /app

# Sync the project into a new environment
RUN uv sync

# Set the command to run your application
CMD ["uv", "run", "my_app", "temperature", "battery_capacity"]