import os
import pytest_asyncio
import asyncpg
from contextlib import asynccontextmanager


# Define an asynchronous context manager for managing the connection pool
@asynccontextmanager
async def create_pool():
    # Retrieve database connection details from environment variables
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    # Create a new connection pool
    pool = await asyncpg.create_pool(
        dsn=f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
        min_size=1,
        max_size=5
    )
    
    try:
        # Yield the pool to the calling context
        yield pool
    finally:
        # Ensure the pool is closed properly
        await pool.close()

# Define a pytest fixture for setting up the database before tests
@pytest_asyncio.fixture(scope="function")
async def db_pool():
    async with create_pool() as pool:
        # Setup database schema
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS measurements (
                    id SERIAL PRIMARY KEY,
                    kind TEXT NOT NULL,
                    time TIMESTAMPTZ NOT NULL,
                    value DOUBLE PRECISION NOT NULL
                )
            ''')
        
        # Yield the pool for use in tests
        yield pool
        
        # Teardown database schema
        async with pool.acquire() as conn:
            await conn.execute("DROP TABLE IF EXISTS measurements")

