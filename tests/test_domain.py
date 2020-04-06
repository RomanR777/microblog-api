from datetime import datetime, timedelta
from microblog_api.domain import Streak, Blocker


def test_first_failed_attempt(user, now, blocker_conf):
    blocker = Blocker(user, *blocker_conf)
    assert False == blocker.is_blocked(False, now)
    assert user.last_failed_signin == now
    assert user.failed_retries == 1


def test_success_login_after_failed_first(user, now, blocker_conf):
    blocker = Blocker(user, *blocker_conf)

    assert False == blocker.is_blocked(False, now)
    assert user.last_failed_signin == now
    assert user.failed_retries == 1

    now = now + timedelta(seconds=30)
    assert False == blocker.is_blocked(True, now)
    assert user.last_failed_signin is None
    assert user.failed_retries == 0


def test_user_blocked(user, now, blocker_conf):
    blocker = Blocker(user, *blocker_conf)

    assert False == blocker.is_blocked(False, now)

    blocking_time = now + timedelta(seconds=20)
    assert False == blocker.is_blocked(False, blocking_time)

    now = blocking_time + timedelta(seconds=20)
    assert True == blocker.is_blocked(False, now)
    assert user.failed_retries == 2
    assert user.last_failed_signin == blocking_time



def test_user_can_login_after_blocking_time_expire(user, now, blocker_conf):
    blocker = Blocker(user, *blocker_conf)
    assert False == blocker.is_blocked(False, now)

    blocking_time = now + timedelta(seconds=20)
    assert False == blocker.is_blocked(False, blocking_time)

    now = blocking_time + timedelta(seconds=20)
    assert True == blocker.is_blocked(False, now)
    assert blocking_time == user.last_failed_signin
    assert user.failed_retries == 2

    now = now + timedelta(seconds=20)
    assert True == blocker.is_blocked(False, now)
    assert blocking_time == user.last_failed_signin
    assert user.failed_retries == 2

    now = now + timedelta(seconds=21)
    assert False == blocker.is_blocked(False, now)


def test_user_steel_blocked_when_login_success(user, now, blocker_conf):
    blocker = Blocker(user, *blocker_conf)
    assert False == blocker.is_blocked(False, now)

    blocking_time = now + timedelta(seconds=20)
    assert False == blocker.is_blocked(False, blocking_time)

    now = blocking_time + timedelta(seconds=20)
    assert True == blocker.is_blocked(True, now)
    assert blocking_time == user.last_failed_signin
    assert user.failed_retries == 2

    now = now + timedelta(seconds=20)
    assert True == blocker.is_blocked(True, now)
    assert blocking_time == user.last_failed_signin
    assert user.failed_retries == 2

    now = now + timedelta(seconds=21)
    assert False == blocker.is_blocked(False, now)


def test_streak_init():
    post_timestamp = datetime(2020, 4, 2, 9, 9, 30, 56)
    streak = Streak('24h')
    streak.add(post_timestamp)
    assert streak.last_publish_timestamp == datetime(2020, 4, 2, 0, 0)
    assert streak.rating == 1


def test_rating_increase():
    post1 = datetime(2020, 4, 2, 9, 9, 30, 56)
    post2 = datetime(2020, 4, 3, 9, 9, 30, 56)
    streak = Streak('24h')
    streak.add(post1)
    assert streak.last_publish_timestamp == datetime(2020, 4, 2, 0, 0)
    streak.add(post2)
    assert streak.last_publish_timestamp == datetime(2020, 4, 3, 0, 0)
    assert streak.rating == 2


def test_rating_not_increasing_for_posts_in_same_period():
    post1 = datetime(2020, 4, 2, 9, 9, 30, 56)
    post2 = datetime(2020, 4, 2, 10, 12, 10, 56)
    streak = Streak('24h')
    streak.add(post1)
    assert streak.last_publish_timestamp == datetime(2020, 4, 2, 0, 0)
    streak.add(post2)
    assert streak.last_publish_timestamp == datetime(2020, 4, 2, 0, 0)
    assert streak.rating == 1

def test_the_dame_instance():
    post1 = datetime(2020, 4, 2, 9, 9, 30, 56)
    post2 = datetime(2020, 4, 3, 10, 12, 10, 56)
    streak = Streak('24h')
    result1 = streak.add(post1)
    result2 = streak.add(post2)
    assert streak == result1
    assert streak == result2

def test_new_instance():
    post1 = datetime(2020, 4, 2, 9, 9, 30, 56)
    post2 = datetime(2020, 4, 3, 10, 12, 10, 56)
    streak = Streak('24h')
    result1 = streak.add(post1)
    result2 = streak.add(post2)
    assert streak == result1
    assert streak == result2
    post3 = datetime(2020, 4, 5, 10, 12, 10, 56)
    result3 = streak.add(post3)
    assert result3 != streak
    assert result3.last_post == datetime(2020, 4, 5, 0, 0)



