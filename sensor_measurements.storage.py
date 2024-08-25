#!/usr/bin/env python3
import argparse
import logging
from aiohttp import web
from writer.main import create_app

logger = logging.getLogger(__name__)

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