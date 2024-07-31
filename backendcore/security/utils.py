"""
Contains methods that otherwise have no home.
"""
import string
import secrets

from datetime import datetime

import backendcore.common.time_fmts as tfmt
import backendcore.data.db_connect as dbc

SALT_LEN = 256


def gen_salt() -> str:
    alphanum = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphanum) for _ in range(SALT_LEN))


def now() -> datetime:
    """
    Generates "now" in UTC.
    """
    return datetime.utcnow()


def naive_now() -> datetime:
    """
    Generates "now" as TZ naive datetime.
    """
    return datetime.now()


def naive_dt_from_db(time_rec=None, time_part=None):
    if not time_part:
        print(f'{time_rec=}')
        time_part = dbc.time_str_from_rec(time_rec)
    print(f'{time_part=}')
    if time_part is None:
        raise ValueError(f'Invalid time record: {time_rec}')
    issue_time = tfmt.iso_time_from_js_time(time_part)
    aware_time = datetime.fromisoformat(str(issue_time))
    return tfmt.aware_time_to_naive_time(aware_time)
