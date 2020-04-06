from aiohttp import web
from .services import SessionService
from aiohttp.web import HTTPForbidden


async def signin_required(request, handler):
    sessionid = request.headers.get('Authorization')
    if not sessionid:
        raise HTTPForbidden()
    srvc = SessionService()
    user_id = await srvc.get_user_id(sessionid)
    if not user_id:
        raise HTTPForbidden()
    request.user_id = user_id
    return True


action_map = {
    'signin_required': signin_required
}


def has_actions(request, handler):
    method = request.method.lower()
    permissions = getattr(handler, 'permissions')
    actions = [actions for methods, actions in permissions.items() if method in methods.lower()]
    actions = [action for subactions in actions for action in subactions]
    not_in_map = set(actions) - set(action_map.keys())
    if not_in_map:
        raise Exception('Not implemented permission!!!')
    return actions


@web.middleware
async def auth_middleware(request, handler):
    if not hasattr(handler, 'permissions'):
        return await handler(request)

    actions = has_actions(request, handler)

    if not actions:
        return await handler(request)

    [await action_map.get(item)(request, handler) for item in actions]

    return await handler(request)
