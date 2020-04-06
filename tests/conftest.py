import pytest
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database
from microblog_api.app import get_app
from microblog_api.models import create_db, db, drop_db, get_db_url
from microblog_api.settings import set_config
from microblog_api.models import User
from datetime import datetime


@pytest.fixture()
async def client(loop, aiohttp_client):
    app_env = ['ignore', 'test']
    set_config(*app_env)

    db_url = get_db_url()
    engine = create_engine(db_url)

    # if database_exists(engine.url):
    #     create_database(engine.url)

    app = get_app(*app_env)
    client_ = await aiohttp_client(app)
    # await db.gino.drop_all()
    # await db.gino.create_all()
    return client_


@pytest.fixture()
def user():
    user = User()
    user.last_failed_signin = None
    user.failed_retries = 0
    return user


@pytest.fixture()
def now():
    return datetime.now()


@pytest.fixture()
def blocker_conf():
    return 2, 60, 300
