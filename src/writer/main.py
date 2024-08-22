# src/fuergy/main.py
from aiohttp import web
from writer.routes import setup_routes
from writer.adapter import init_db, close_db, init_tables

async def on_startup(app: web.Application) -> None:
    await init_db(app)
    await init_tables(app['db_pool'])

async def on_cleanup(app: web.Application) -> None:
    await close_db(app)

def create_app() -> web.Application:
    app = web.Application()
    app['config'] = {
        'database_url': 'postgresql://user:password@localhost:5432/measurements_db'
    }
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    setup_routes(app)
    return app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app)
