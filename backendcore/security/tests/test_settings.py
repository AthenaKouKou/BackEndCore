import datetime

import backendcore.security.settings as stg

# I can't imagine giving them less than five minutes to use the link.
MIN_RESET_SECONDS = 5 * 60


def test_get_pw_reset_ttl_seconds():
    assert stg.get_pw_reset_ttl_seconds() > MIN_RESET_SECONDS


def test_get_auth_key_ttl():
    assert isinstance(stg.get_auth_key_ttl(), datetime.timedelta)


def test_get_pw_reset_ttl():
    assert isinstance(stg.get_pw_reset_ttl(), datetime.timedelta)
