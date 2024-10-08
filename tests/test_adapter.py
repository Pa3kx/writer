import pytest
import asyncpg
from writer.adapter import store_measurements, get_measurements, Measurement

pytestmark = pytest.mark.asyncio(loop_scope="function")


async def test_store_measurements(db_pool):
    """
    Test storing measurements into the database.
    Ensures that data is correctly inserted and matches expectations.
    """
    measurements = [
        Measurement(kind="temperature", time=1627848484, value=23.5),
        Measurement(kind="humidity", time=1627848485, value=55.2),
    ]

    await store_measurements(db_pool, measurements)
    async with db_pool.acquire() as conn:
        rows: list[asyncpg.Record] = await conn.fetch(
            "SELECT kind, extract(epoch from time) as time, value FROM measurements"
        )
        assert len(rows) == 2
        row1: asyncpg.Record = rows[0]
        row2: asyncpg.Record = rows[1]
        assert row1["kind"] == "temperature"
        assert row1["time"] == 1627848484
        assert row1["value"] == 23.5
        assert row2["kind"] == "humidity"
        assert row2["time"] == 1627848485
        assert row2["value"] == 55.2


async def test_get_measurements(db_pool):
    """
    Test retrieving measurements from the database.
    Ensures that data is retrieved correctly based on the specified time range and kind.
    """
    async with db_pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO measurements(kind, time, value)
            VALUES($1, to_timestamp($2), $3)
        """,
            [
                ("temperature", 1627848484, 23.5),
                ("humidity", 1627848485, 55.2),
            ],
        )

    result = await get_measurements(
        db_pool, ["temperature", "humidity"], 1627848480, 1627848490
    )
    assert "temperature" in result
    assert "humidity" in result
    assert len(result["temperature"]) == 1
    assert len(result["humidity"]) == 1
    assert result["temperature"][0].value == 23.5
    assert result["humidity"][0].value == 55.2


async def test_get_measurements_no_match(db_pool):
    """
    Test retrieving measurements when no data matches the query.
    Ensures that the function correctly returns an empty result.
    """
    result = await get_measurements(db_pool, ["temperature"], 1627848480, 1627848490)

    assert result == {}


async def test_get_measurements_invalid_kind(db_pool):
    """
    Test retrieving measurements with an invalid kind.
    Ensures the function handles invalid kinds gracefully.
    """
    async with db_pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO measurements(kind, time, value)
            VALUES($1, to_timestamp($2), $3)
        """,
            [
                ("temperature", 1627848484, 23.5),
            ],
        )
    result = await get_measurements(db_pool, [""], 1627848484, 1627848485)

    assert result == {}
