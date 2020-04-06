import os
import hashlib
import json
from datetime import datetime
from sqlalchemy import and_
from .schemas import (PostSerializer, PostDetailSerializer,
                      SigupSchema, SiginSchema)
from .models import Post, User, Session, Tag, TagXPost, Rating
from marshmallow.exceptions import ValidationError
from aiohttp.web import HTTPBadRequest
from .domain import Blocker

PASSWORD_SALT = 'passwordsalt'
SESSION_SALT = 'sessionsalt'


class BaseService:
    def serialize(self, claz, data, many=False):
        validator = claz()
        valid_data = None
        try:
            if isinstance(data, str):
                valid_data = validator.loads(data, many=many)
            if isinstance(data, dict):
                valid_data = validator.load(data, many=many)
        except ValidationError:
            raise HTTPBadRequest(body=json.dumps(validator.error_messages))
        return valid_data


class SessionService(BaseService):
    async def create(self, user: User) -> dict:
        usersession = await Session.query.where(Session.user_id == user.id).gino.first()
        if usersession:
            await usersession.delete()
        session_hash = hashlib.pbkdf2_hmac('sha256',
                                           bytes(user.email, 'utf8'),
                                           bytes(user.nickname, 'utf8'), 100).hex()
        await Session.create(sessionid=session_hash, user_id=user.id)
        return {'sessionid': session_hash}

    async def get_user_id(self, sessionid: str) -> dict:
        session_data = await Session.query.where(Session.sessionid == sessionid).gino.first()
        if not session_data:
            return None
        return session_data.to_dict()['user_id']


class UserService(BaseService):
    def hash_password(self, password):
        return hashlib.pbkdf2_hmac('sha256',
                                   bytes(password, 'utf8'),
                                   bytes(PASSWORD_SALT, 'utf8'), 100).hex()

    async def signup(self, data):
        data = self.serialize(SigupSchema, data)
        data['password'] = self.hash_password(data['password'])
        result = await User.create(**data)
        data = self.serialize(SigupSchema, result)
        return data

    def check_password(self, user: User, password: str) -> bool:
        return user.password == self.hash_password(password)

    def check_blocking(self, user: User, signin_result: bool) -> bool:
        attempt_count = int(os.environ.get('SIGIN_ATTEMPT_COUNT_RESTRICTION'))
        attempt_period = int(os.environ.get('SIGIN_ATTEMPT_TIME_PERIOD_RESTRICTION_SEC'))
        block_period = int(os.environ.get('SIGN_ATTEMPT_BLOCKING_PERIOD_SEC'))
        now = datetime.now()
        blocker = Blocker(user, attempt_count, attempt_period, block_period)
        return blocker.is_blocked(signin_result, now)

    async def signin(self, data):
        data = self.serialize(SiginSchema, data)
        user = await User.query.where(User.email == data['email']).gino.first()
        if not user:
            return None
        sign_result = self.check_password(user, data['password'])
        is_blocked = self.check_blocking(user, sign_result)
        if is_blocked:
            return None
        if not sign_result:
            return None
        session_srvc = SessionService()
        return await session_srvc.create(user)

    def rating(self):
        pass


class PostService(BaseService):
    async def create(self, data):
        data = self.serialize(PostSerializer, data)
        tags = await Tag.create_all(data.pop('tags'))
        post = await Post.create(**data)
        TagXPost.create_all(post, tags)
        Rating.query(and_(Rating.user_id == data['user_id'],
                          Rating.type_.in_(Rating.types.keys())))
        resp_data = self.serialize(PostSerializer, post)
        return resp_data

    async def list(self, data):
        posts = await Post.query.gino.all()
        serializer = PostDetailSerializer()
        posts = serializer.dumps([post.to_dict() for post in posts], many=True)
