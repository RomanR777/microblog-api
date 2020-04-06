import pytest
import os
import json
import time
from freezegun import freeze_time
from datetime import datetime
from microblog_api.models3 import User, SIGNIN_STATUSES



email = 'test@test.com'
password = 'Test_Test_111'
wrong_password = 'wrongpassword'

signup = {'email': email,
            'password1': password,
            'password2': password
            }
signup_json = json.dumps(signup)
signin_json = json.dumps({'email': email, 'password': 'password'})

headers = {'Content-Type': 'application/json'}


async def test_user_model_signup(client):
    user = await User.signup(email, password)
    assert user is not None
    assert user['email'] == email


async def test_user_model_signin(client):
    user = await User.signup(email, password)
    assert user is not None
    status, session_id = await User.signin(email, password)
    assert status == SIGNIN_STATUSES.SUCCESS
    assert session_id == 'sesionid'


async def test_signin_blocked_after_5_retries(client):
    user = await User.signup(email, password)
    assert user is not None
    for _ in range(7):
        status, session_id = await User.signin(email, wrong_password)
    assert status == SIGNIN_STATUSES.BLOCKED
    assert session_id is None


async def test_user_can_login_after_block_period_expired(client, monkeypatch):
    user = await User.signup(email, password)
    assert user is not None

    with freeze_time('2020-04-01 00:00:00'):
        status, session_id = await User.signin(email, wrong_password)
        assert status == SIGNIN_STATUSES.INCORECT_PASSWORD

    with freeze_time('2020-04-01 00:00:03'):
        status, session_id = await User.signin(email, wrong_password)
        assert status == SIGNIN_STATUSES.INCORECT_PASSWORD

    with freeze_time('2020-04-01 00:00:05'):
        status, session_id = await User.signin(email, wrong_password)
        assert status == SIGNIN_STATUSES.BLOCKED


async def test_signup(client):
    resp = await client.post('/v1/users/signup',
                             data=signup_json,
                             headers=headers)
    assert resp.status == 201


async def test_signin(client):
    resp = await client.post('/v1/users/sigin',
                             data=signin_json,
                             headers=headers)
    assert resp.status == 201


async def test_signout(client):
    resp = await client.delete('/v1/users/signout', headers=headers)
    assert resp.status == 200

def test_signin_blocking():
    user = User()

    assert True == True