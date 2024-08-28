from aiohttp import web
from pydantic import ValidationError
from writer.adapter import store_measurements, get_measurements, Measurement
import logging

logger = logging.getLogger(__name__)

async def store_measurements_handler(request: web.Request) -> web.Response:
    """
    ---
    summary: Store sensor measurements
    tags:
      - measurements
    parameters:
      - in: path
        name: kind
        schema:
          type: string
        required: true
        description: Measurement type
      - in: body
        name: body
        description: Measurement data
        required: true
        schema:
          type: object
          properties:
            values:
              type: array
              items:
                type: object
                properties:
                  time:
                    type: integer
                  value:
                    type: number
    responses:
      '204':
        description: Measurements stored successfully
      '400':
        description: Invalid input
      '500':
        description: Server error
    """
    kind = request.match_info["kind"]
    measurement_kinds = request.app["config"]["measurement_kinds"]
    if kind not in measurement_kinds:
        return web.json_response(
            status=400,
            data={
                "error": f"Invalid measurement type {kind}",
                "valid_types": " ".join(measurement_kinds),
            },
        )

    try:
        data = await request.json()
        measurements = [
            Measurement(kind=kind, time=m["time"], value=m["value"])
            for m in data["values"]
        ]
    except ValidationError as ve:
        return web.json_response(status=400, data={"error": ve.errors()})
    except KeyError as ke:
        return web.json_response(
            status=400,
            data={"error": f"Missing attribute in measurement input data: {str(ke)}"},
        )
    except Exception as e:
        logger.debug(f"Exception storing measurements: {e}")
        return web.json_response(status=500)

    await store_measurements(request.app["db_pool"], measurements)
    return web.Response(status=204)


async def get_measurements_handler(request: web.Request) -> web.Response:
    """
    ---
    summary: Get sensor measurements
    tags:
      - measurements
    parameters:
      - in: query
        name: kind
        schema:
          type: array
          items:
            type: string
        required: true
        description: Measurement types to retrieve
      - in: query
        name: from_time
        schema:
          type: integer
        required: true
        description: Start timestamp (Unix time)
      - in: query
        name: to_time
        schema:
          type: integer
        required: true
        description: End timestamp (Unix time)
    responses:
      '200':
        description: Measurements retrieved successfully
      '400':
        description: Invalid input
      '500':
        description: Server error
    """
    try:
        kinds = request.query.getall("kind")
        from_time = int(request.query["from_time"])
        to_time = int(request.query["to_time"])

    except (KeyError, ValueError):
        return web.Response(status=400)
    except Exception as e:
        logger.debug(f"Exception retrieving measurements: {e}")
        return web.Response(status=500)

    measurements = await get_measurements(
        request.app["db_pool"], kinds, from_time, to_time
    )
    result = {k: [m.model_dump() for m in v] for k, v in measurements.items()}
    return web.json_response(result)

def setup_routes(app: web.Application) -> None:
    app.router.add_post("/api/v1/measurements/{kind}", store_measurements_handler)
    app.router.add_get("/api/v1/measurements", get_measurements_handler)
