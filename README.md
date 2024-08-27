# 🖋️ Writer

**Writer** is a Python-based service that stores sensor measurements into a PostgreSQL database. It provides an HTTP REST API to write and read sensor measurements, supporting various types of measurements, each represented as a time series.

🚧 **Status**: Ready & Tests passing (Hours spent: ~20). Final polish done throughout the day (27.8.2024)

## ✨ Features

- 📝 **Store sensor measurements**: Handles multiple types of sensor measurements, each represented as a time series. Initialzied as a list of strings on service start
- 📊 **Read sensor data**: Retrieve sensor data within specified time intervals.

## 📦 Requirements

- 🐍 [Python](https://www.python.org/) 3.12+
- 🐘 [PostgreSQL](https://www.postgresql.org/) + [asyncpg](https://magicstack.github.io/asyncpg/current/) - Write heavy environment requires postgres instead of sqlite
- 🐳 [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) - Setup, build, run containers
- ⚡ [uv](https://astral.sh/blog/uv-unified-python-packaging) - Next gen python packaging manager
- 🌐 [AIOHTTP](https://docs.aiohttp.org/en/stable/) - Web server
- 🛠️ [Pydantic](https://docs.pydantic.dev/latest/) - Data validation
- 🧪 [Pytest](https://docs.pytest.org/en/stable/) + [asyncio](https://pytest-asyncio.readthedocs.io/en/latest/) & [aiohttp](https://docs.aiohttp.org/en/v3.7.4/testing.html/)- Testing frameworks

## 🚀 Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Pa3kx/writer.git
   cd writer
   docker-compose up --build # Run showcase
   docker-compose -f docker-compose.yml -f docker-compose.test.yml up --build # Run tests