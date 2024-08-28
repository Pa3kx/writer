import os
import pytest_asyncio
import asyncpg
from contextlib import asynccontextmanager


@asynccontextmanager
async def create_pool():
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    pool = await asyncpg.create_pool(
        dsn=f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
        min_size=1,
        max_size=5,
    )

    try:
        yield pool
    finally:
        await pool.close()


@pytest_asyncio.fixture(scope="function")
async def db_pool():
    async with create_pool() as pool:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS measurements (
                    id SERIAL PRIMARY KEY,
                    kind TEXT NOT NULL,
                    time TIMESTAMPTZ NOT NULL,
                    value DOUBLE PRECISION NOT NULL
                )
            """
            )

        yield pool

        async with pool.acquire() as conn:
            await conn.execute("DROP TABLE IF EXISTS measurements")
