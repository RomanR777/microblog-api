from datetime import timedelta, datetime


class Blocker:
    def __init__(self, user, attempt_count, attempt_period, block_period):
        self.user = user
        self.attempt_count = attempt_count
        self.attempt_period = attempt_period
        self.block_period = block_period

    def is_attempt_in_blocking_period(self, now):
        if self.user.last_failed_signin is None:
            return False

        time_restriction = self.user.last_failed_signin + timedelta(
            seconds=self.attempt_period)

        if self.user.last_failed_signin < now <= time_restriction \
                and self.user.failed_retries == self.attempt_count:
            return True
        else:
            return False

    def increase_attempt(self, now):
        if self.user.failed_retries <= self.attempt_count:
            self.user.failed_retries += 1
            self.user.last_failed_signin = now

    def release_blocking(self):
        self.user.failed_retries = 0
        self.user.last_failed_signin = None

    def is_blocked(self, attempt_result: bool, now: datetime) -> bool:
        """
        Purpose of method determine is user blocked or not
        :param login_result: if user successful logged in True otherwise False
        :param now: datetime when login happen
        :return: True if user blocked
        """
        in_blocking = self.is_attempt_in_blocking_period(now)
        if in_blocking:
            return True

        if not attempt_result:
            self.increase_attempt(now)
            return self.is_attempt_in_blocking_period(now)
        else:
            self.release_blocking()
            return False


class Streak:
    last_publish_timestamp = None
    rating = None
    types = {'24h': {'reset': {'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0},
                     'value': 24,
                     'attr': 'days'},
             '1h': {'reset': {'minute': 0, 'second': 0, 'microsecond': 0},
                    'value': 1,
                    'attr': 'hours'}
             }

    def __init__(self, type_):
        self.type_ = type_

    def __reset_timestamp(self, timestamp):
        reset = self.types[self.type_]['reset']
        return timestamp.replace(**reset)

    def __diff(self, end, start):
        end = self.__reset_timestamp(end)
        start = self.__reset_timestamp(start)
        attr = self.types[self.type_]['attr']
        return getattr(end - start, attr)

    def add(self, timestamp: datetime):
        timestamp = self.__reset_timestamp(timestamp)
        if self.last_publish_timestamp is None:
            self.last_publish_timestamp = timestamp
            self.rating = 1
            return self

        if timestamp <= self.last_publish_timestamp:
            return self

        delta = self.__diff(timestamp, self.last_publish_timestamp)

        if delta == 1:
            self.last_publish_timestamp = timestamp
            self.rating = self.rating + delta
            return self
        else:
            return Streak(self.type_).add(timestamp)
