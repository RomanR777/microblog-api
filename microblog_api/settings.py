import os
import pathlib
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).parent.parent


def set_config(*cmdline_args):
    if len(cmdline_args) < 2:
        env = 'dev'
    else:
        env = cmdline_args[1]

    config_path = BASE_DIR / 'config' / f'env-{env}'
    load_dotenv(config_path.as_posix())


def get_config():
    return {'HOST': os.environ.get('HOST'),
            'PORT': os.environ.get('PORT'),
            'DB_HOST': os.environ.get('DB_HOST'),
            'DB_PORT': os.environ.get('DB_PORT'),
            'DB_NAME': os.environ.get('DB_NAME'),
            'DB_USER': os.environ.get('DB_USER'),
            'DB_PASSWORD': os.environ.get('DB_PASSWORD'),
            'DB_POOL_MIN': os.environ.get('DB_POOL_MIN'),
            'DB_POOL_MAX': os.environ.get('DB_POOL_MAX'),
            'DB_TYPE': os.environ.get('DB_TYPE'),
            'GINO_DRIVER': os.environ.get('GINO_DRIVER'),
            'SIGIN_ATTEMPT_COUNT_RESTRICTION': int(os.environ.get('SIGIN_ATTEMPT_COUNT_RESTRICTION')),
            'SIGIN_ATTEMPT_TIME_PERIOD_RESTRICTION_SEC': int(
                os.environ.get('SIGIN_ATTEMPT_TIME_PERIOD_RESTRICTION_SEC')),
            'SIGN_ATTEMPT_BLOCKING_PERIOD_SEC': int(os.environ.get('SIGN_ATTEMPT_BLOCKING_PERIOD_SEC')),
            }


def get_db_url():
    config = get_config()
    db_url = '{DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'.format(
        DRIVER=config['DB_TYPE'],
        DB_USER=config['DB_USER'],
        DB_PASSWORD=config['DB_PASSWORD'],
        DB_HOST=config['DB_HOST'],
        DB_PORT=config['DB_PORT'],
        DB_NAME=config['DB_NAME']
    )
    return db_url
