import logging
import sys
import os
from aiohttp import web

from microblog_api.settings import set_config
from microblog_api.routes import setup_routes
from .models import db
from .middlewares import auth_middleware


def get_gino_config():
    gino_conf = {'host': os.environ.get('DB_HOST'),
                 'port': os.environ.get('DB_PORT'),
                 'driver': os.environ.get('GINO_DRIVER'),
                 'user': os.environ.get('DB_USER'),
                 'password': os.environ.get('DB_PASSWORD'),
                 'database': os.environ.get('DB_NAME'),
                 'pool_min_size': int(os.environ.get('DB_POOL_MIN')),
                 'pool_max_size': int(os.environ.get('DB_POOL_MAX'))}
    return gino_conf


async def init_db(_):
    await db.gino.drop_all()
    await db.gino.create_all()


def get_app(*args):
    set_config(*args)
    app = web.Application(middlewares=[db, auth_middleware])
    db.init_app(app, config=get_gino_config())
    setup_routes(app)
    app.on_startup.append(init_db)
    return app


def run_app(*args):
    app = get_app(*args)
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app,
                host=os.environ.get('HOST'),
                port=os.environ.get('PORT'))


if __name__ == '__main__':
    run_app(*sys.argv)
