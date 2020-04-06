from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database
from microblog_api.settings import get_db_url
from gino.ext.aiohttp import Gino


def create_db():
    db_url = get_db_url()
    engine = create_engine(db_url)
    if not database_exists(engine.url):
        create_database(engine.url)


def drop_db():
    db_url = get_db_url()
    engine = create_engine(db_url)
    if database_exists(engine.url):
        drop_database(engine.url)


async def create_schema():
    db_url = get_db_url()
    engine = create_engine(db_url)
    await db.set_bind(engine)
    await db.create_all()


async def init_db(app):
    db_url = get_db_url()
    await db.set_bind(db_url)
    await db.create_all()
    app['db'] = db


async def close_db(app):
    app['db'].bind.dispose()


db = Gino()


class Session(db.Model):
    __tablename__ = 'sessions'
    # id = db.Column(db.Integer(), primary_key=True)
    sessionid = db.Column(db.Unicode(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    session_unique = db.UniqueConstraint("sessionid", "user_id")


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.Unicode(), unique=True)
    password = db.Column(db.Unicode(), unique=True)
    nickname = db.Column(db.Unicode(), unique=True)
    last_failed_signin = db.Column(db.DateTime(), nullable=True)
    failed_retries = db.Column(db.Integer(), default=0)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Unicode())
    name_unique = db.UniqueConstraint("name")

    @classmethod
    async def create_all(cls, tags: list) -> list:
        new_tags = [item for item in tags if item]
        existing_tags = await Tag.query.where(Tag.name.in_(new_tags)).gino.all()
        existing_tag_names = [tag.name for tag in existing_tags]
        if existing_tag_names:
            new_tags = set(new_tags) - set(existing_tag_names)
        if not new_tags:
            return existing_tags
        hashed_tags = {item for item in new_tags if item and item.startswith('#')}
        hashed_tags = hashed_tags or set()
        tag_names = ['#' + item for item in set(new_tags) - hashed_tags]
        tag_names.extend(hashed_tags)
        insertion_data = [dict(name=item) for item in tag_names]
        await Tag.insert().gino.all(insertion_data)
        existing_tag_names.extend(tag_names)
        result = await Tag.query.where(Tag.name.in_(existing_tag_names)).gino.all()
        return result


class TagXPost(db.Model):
    __tablename__ = 'tagXpost'
    id = db.Column(db.Integer(), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @classmethod
    async def create_all(cls, post, tags):
        insertion_data = [dict(tag_id=tag.id, post_id=post.id) for tag in tags]
        await Tag.insert().gino.all(insertion_data)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.Unicode())
    body = db.Column(db.Unicode())
    is_published = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer(), primary_key=True)
    type_ = db.Column(db.Unicode())
    last_publish_timestamp = db.Column(db.DateTime())
    rating = db.Column(db.Integer())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
