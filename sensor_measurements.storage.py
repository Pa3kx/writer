#!/usr/bin/env python3
import os
import argparse
import logging
from aiohttp import web
from routes import setup_routes, set_accepted_measurement_kinds
from adapter import init_db, close_db, init_tables

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
        "measurement_kinds": measurement_kinds
    }
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    setup_routes(app)
    set_accepted_measurement_kinds(measurement_kinds)
    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description="Sensor Measurements Storage Service",
    usage="./sensor_measurements.storage.py sensor_temperature battery_capacity",
    epilog="Please specify at least one measurement type."
)
    parser.add_argument('measurement_kinds', nargs='+', help='List of measurement types to support')
    parser.add_argument("--log-level", default="ERROR", help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, NONE)")
    args = parser.parse_args()

    measurement_kinds = args.measurement_kinds

    if args.log_level.upper() == "NONE":
        log_level = logging.CRITICAL + 1
    else:
        log_level = getattr(logging, args.log_level.upper(), logging.WARNING)

    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger.debug(f"Starting service with measurement types: {measurement_kinds}")
    app = create_app(measurement_kinds)
    web.run_app(app, host="0.0.0.0", port=8080)
