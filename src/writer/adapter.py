import os
from pydantic import BaseModel, Field, ValidationError
import asyncpg
from aiohttp import web
import logging

logger = logging.getLogger(__name__)

class Measurement(BaseModel):
    kind: str = Field(..., description="Kind of the measurement (e.g., temperature)")
    time: int = Field(..., ge=0, description="Unix timestamp in seconds")
    value: float = Field(..., description="The sensor measurement value")

async def init_db(app: web.Application) -> None:
    """Initialize the database connection pool."""
    app['db_pool'] = await asyncpg.create_pool(
        dsn=f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )

async def close_db(app: web.Application) -> None:
    """Close the database connection pool."""
    pool: asyncpg.Pool | None = app.get('db_pool')
    if pool:
        await pool.close()

async def init_tables(pool: asyncpg.Pool) -> None:
    """Create the necessary tables in the database."""
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id SERIAL PRIMARY KEY,
                kind TEXT NOT NULL,
                time TIMESTAMPTZ NOT NULL,
                value DOUBLE PRECISION NOT NULL
            )
        ''')

async def store_measurements(
    pool: asyncpg.Pool, 
    measurements: list[Measurement]
) -> None:
    """Store measurements into the database."""
    async with pool.acquire() as conn:
        try:
            async with conn.transaction():
                await conn.executemany(
                    '''
                    INSERT INTO measurements(kind, time, value)
                    VALUES($1, to_timestamp($2), $3)
                    ''', 
                    [(m.kind, m.time, m.value) for m in measurements]
                )
        except Exception as e:
            logger.error(f"Error in transaction: {e}")
            await conn.rollback()
            raise

async def get_measurements(
    pool: asyncpg.Pool, 
    kinds: list[str], 
    from_time: int, 
    to_time: int
) -> dict[str, list[Measurement]]:
    """Retrieve measurements from the database."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            '''
            SELECT kind, extract(epoch from time) as time, value
            FROM measurements
            WHERE kind = ANY($1::text[])
            AND time BETWEEN to_timestamp($2) AND to_timestamp($3)
            ORDER BY time ASC
            ''', 
            kinds, from_time, to_time
        )

        result: dict[str, list[Measurement]] = {}

        for row in rows:
            row : asyncpg.Record
            measurement = Measurement(
                kind=row['kind'],
                time=row['time'], 
                value=row['value']
            )
            if row['kind'] not in result:
                result[row['kind']] = []
            result[row['kind']].append(measurement)

        return result
