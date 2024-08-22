# tests/test_adapter.py

import pytest
import asyncpg
from writer.adapter import store_measurements, get_measurements, Measurement

@pytest.fixture(scope="session")
async def db_pool():
    """
    Fixture to set up a connection pool to a test database.
    Ensures isolation for each test by using a transaction or creating/dropping tables as needed.
    """
    #TODO setup env vars and test db
    pool = await asyncpg.create_pool(dsn="postgresql://user:password@db:5432/test_database")

    
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                id SERIAL PRIMARY KEY,
                kind TEXT NOT NULL,
                time TIMESTAMPTZ NOT NULL,
                value REAL NOT NULL
            )
        ''')
    
    yield pool 

    # Clean up: drop the table after the test
    async with pool.acquire() as conn:
        await conn.execute("DROP TABLE IF EXISTS measurements")
    
    await pool.close()

@pytest.mark.asyncio
async def test_store_measurements(db_pool):
    """
    Test storing measurements into the database.
    Ensures that data is correctly inserted and matches expectations.
    """
    # Sample data
    measurements = [
        Measurement(kind="temperature", time=1627848484, value=23.5),
        Measurement(kind="humidity", time=1627848485, value=55.2),
    ]

    # Execute the function to store measurements
    await store_measurements(db_pool, measurements)

    # Verify the data was stored correctly
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT kind, extract(epoch from time) as time, value FROM measurements")
        assert len(rows) == 2
        assert rows[0]['kind'] == "temperature"
        assert rows[0]['time'] == 1627848484
        assert rows[0]['value'] == 23.5
        assert rows[1]['kind'] == "humidity"
        assert rows[1]['time'] == 1627848485
        assert rows[1]['value'] == 55.2

@pytest.mark.asyncio
async def test_get_measurements(db_pool):
    """
    Test retrieving measurements from the database.
    Ensures that data is retrieved correctly based on the specified time range and kind.
    """
    # Insert sample data intI hao the database
    async with db_pool.acquire() as conn:
        await conn.executemany('''
            INSERT INTO measurements(kind, time, value)
            VALUES($1, to_timestamp($2), $3)
        ''', [
            ("temperature", 1627848484, 23.5),
            ("humidity", 1627848485, 55.2),
        ])

    # Retrieve the data using the function
    result = await get_measurements(db_pool, ["temperature", "humidity"], 1627848480, 1627848490)

    # Verify that the data was retrieved correctly
    assert "temperature" in result
    assert "humidity" in result
    assert len(result["temperature"]) == 1
    assert len(result["humidity"]) == 1
    assert result["temperature"][0].value == 23.5
    assert result["humidity"][0].value == 55.2

@pytest.mark.asyncio
async def test_get_measurements_no_match(db_pool):
    """
    Test retrieving measurements when no data matches the query.
    Ensures that the function correctly returns an empty result.
    """
    # Retrieve data from an empty database
    result = await get_measurements(db_pool, ["temperature"], 1627848480, 1627848490)

    # Verify that the result is empty
    assert result == {}

@pytest.mark.asyncio
async def test_get_measurements_invalid_kind(db_pool):
    """
    Test retrieving measurements with an invalid kind.
    Ensures the function handles invalid kinds gracefully.
    """
    # Insert sample data into the database
    async with db_pool.acquire() as conn:
        await conn.executemany('''
            INSERT INTO measurements(kind, time, value)
            VALUES($1, to_timestamp($2), $3)
        ''', [
            ("temperature", 1627848484, 23.5),
        ])

    # Query with an invalid kind
    result = await get_measurements(db_pool, [""], 1627848484, 1627848485)
    
    # Verify that the result is empty
    assert result == {}


@pytest.mark.asyncio
async def test_store_measurements_invalid_data(db_pool):
    """
    Test storing measurements with invalid data.
    Ensures that invalid data is not inserted into the database.
    """
    # Sample invalid data (missing 'kind')
    measurements = [
        Measurement(kind=None, time=1627848484, value=23.5)
    ]

    # Attempt to store invalid measurements and expect an exception
    with pytest.raises(Exception):
        await store_measurements(db_pool, measurements)
