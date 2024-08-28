import os
import logging
from aiohttp import web
from writer.routes import setup_routes
from writer.adapter import init_db, close_db, init_tables
from aiohttp_swagger import setup_swagger
logger = logging.getLogger(__name__)


async def on_startup(app: web.Application) -> None:
    logger.debug("Initializing database...")
    await init_db(app)
    await init_tables(app["db_pool"])
    logger.info("Database initialized successfully.")


async def on_cleanup(app: web.Application) -> None:
    logger.debug("Closing database connection...")
    await close_db(app)
    logger.info("Database connection closed successfully.")


def create_app(measurement_kinds: list[str]) -> web.Application:
    app = web.Application()

    db_user = os.getenv("TEST_DB_USER")
    db_password = os.getenv("TEST_DB_PASSWORD")
    db_host = os.getenv("TEST_DB_HOST")
    db_port = os.getenv("TEST_DB_PORT")
    db_name = os.getenv("TEST_DB_NAME")

    app["config"] = {
        "database_url": f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
        "measurement_kinds": measurement_kinds,
    }
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    setup_routes(app)
    setup_swagger(
        app,
        swagger_url="/api/v1/doc",
        title="Sensor Measurements API",
        description="API for storing and retrieving sensor measurements",
        api_version="0.1.0"
    )
    return app
