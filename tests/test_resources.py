import json
from microblog_api.models import User

post_fixture = {'title': 'test title',
                'body': 'test body'}


headers = {'Content-Type': 'application/json'}

data = {'email': 'test@test.com',
            'nickname': 'test0',
            'password': 'password'
            }

signin_data = {'email': 'test@test.com',
               'password': 'password'}

not_valid_post = {'title': 'test title',
                  'body': 'post content'}

post1 = {'title': 'test title',
         'body': 'post content',
         'tags': ['#tag1', '#tag2', '#tag3']
         }

post2 = {'title': 'test title',
         'body': 'post content',
         'tags': ['#tag1']
         }


async def test_signup(client):
    resp = await client.post('/v1/users/signup', json=json.dumps(data))
    assert resp.status == 200
    user = await User.query.where(User.nickname == data['nickname']).gino.first()
    assert user.email == data['email']


async def test_signin(client):
    resp = await client.post('/v1/users/signup', json=json.dumps(data))
    assert resp.status == 200
    resp = await client.post('/v1/users/signin', json=json.dumps(signin_data))
    assert resp.status == 200
    session_obj = await resp.json()
    assert len(session_obj.get('sessionid')) == 64


async def get_session(client):
    await client.post('/v1/users/signup', json=json.dumps(data))
    resp = await client.post('/v1/users/signin', json=json.dumps(signin_data))
    resp_data = await resp.json()
    return resp_data['sessionid']


async def test_autorization_error_no_auth_header(client):
    resp = await client.post('/v1/posts', json=json.dumps(post1))
    assert resp.status == 403


async def test_autorization_error_not_valid_sessionid(client):
    headers = {'Authorization': 'sessionid'}
    resp = await client.post('/v1/posts', json=json.dumps(post1), headers=headers)
    assert resp.status == 403


async def test_post_valid(client):
    sessionid = await get_session(client)
    headers = {'Authorization': sessionid}
    resp = await client.post('/v1/posts', json=json.dumps(post1), headers=headers)
    assert resp.status == 201

async def test_post_test(client):
    resp = await client.post('/v1/posts', json=json.dumps(post1))
    assert resp.status == 201
