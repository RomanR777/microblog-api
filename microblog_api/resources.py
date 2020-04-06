import json
from aiohttp.web import View, json_response
from aiohttp.web import HTTPForbidden
from .services import UserService, PostService


class SigninView(View):
    async def post(self):
        service = UserService()
        data = await self.request.json()
        resp_data = await service.signin(data)
        if not resp_data:
            raise HTTPForbidden()
        return json_response(resp_data, status=200)


class SignupView(View):
    async def post(self):
        service = UserService()
        data = await self.request.json()
        resp_data = await service.signup(data)
        return json_response(resp_data)


class UsersRatingView(View):
    async def get(self):
        service = UserService()
        data = service.rating()
        return json_response(data)


class PostListCreateView(View):
    permissions = {'POST': ['signin_required']}

    async def post(self):
        service = PostService()
        data = json.loads(await self.request.json())
        data['user_id'] = self.request.user_id
        resp_data = await service.create(data)
        return json_response(resp_data)

    async def get(self):
        service = PostService()
        data = self.request.query
        resp_data = service.list(data)
        return json_response(resp_data)


class PostUpdateDeleteView(View):
    permissions = {'GET, PUT': ['signin_required']}

    async def put(self):
        service = PostService()
        data = await self.request.json()
        resp_data = service.update(data)
        return json_response(resp_data)

    async def get(self):
        service = PostService()
        data = self.request.json()
        resp_data = service.update(data)
        return json_response(resp_data)
