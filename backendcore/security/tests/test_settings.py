import datetime

import backendcore.security.settings as stg


def test_get_auth_key_ttl():
    assert isinstance(stg.get_auth_key_ttl(), datetime.timedelta)


def test_get_pw_reset_ttl():
    assert isinstance(stg.get_pw_reset_ttl(), datetime.timedelta)
