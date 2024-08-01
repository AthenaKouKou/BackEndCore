import os
from datetime import timedelta

import backendcore.common.time_fmts as tfmt

# Giving the user lots of time until we sort out what TZ we are in!
AUTH_KEY_TTL = timedelta(minutes=int(os.getenv('AUTH_KEY_TTL',
                                               tfmt.MINS_PER_DAY)))

PW_RESET_TOK_TTL = timedelta(minutes=int(os.getenv('PW_RESET_TOK_TTL',
                                                   tfmt.MINS_PER_DAY)))


def get_auth_key_ttl():
    return AUTH_KEY_TTL


def get_pw_reset_ttl():
    return PW_RESET_TOK_TTL


def get_pw_reset_ttl_seconds():
    day_seconds = get_pw_reset_ttl().days * tfmt.SECONDS_PER_DAY
    return day_seconds + get_pw_reset_ttl().seconds


def main():
    print(f'{AUTH_KEY_TTL=}')
    print(f'{PW_RESET_TOK_TTL=}')


if __name__ == '__main__':
    main()
