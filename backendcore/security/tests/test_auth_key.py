# Copyright 2021 API MixMaster LLC. All rights reserved.
"""
Tests auth_key.py
"""
import os

from datetime import datetime, timedelta
from unittest import mock

import pytest

from backendcore.env.env_utils import is_cicd_env
from backendcore.security.utils import now
from backendcore.security.settings import get_auth_key_ttl
import backendcore.users.query as uqry

import backendcore.security.auth_key as akey


def get_issue_time(user):
    issue_time = user.get(uqry.ISSUE_TIME)
    if isinstance(issue_time, str):
        return akey.naive_dt_from_db(time_part=user.get(uqry.ISSUE_TIME))
    elif isinstance(issue_time, dict):
        return akey.naive_dt_from_db(time_rec=user.get(uqry.ISSUE_TIME))
    else:
        raise ValueError(f'get_issue_time() passed a bad time: {issue_time}')


@pytest.fixture(scope='function')
def temp_user():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    NO_LISTS_REASON = "DB does not support lists as values"
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    print(f'{LISTS_IN_DB=}')
    print(f'{os.environ.get('LISTS_IN_DB')=}')

    try:
        uqry.delete(uqry.TEST_EMAIL)
    except Exception:
        print('User was not already in DB')
    mongo_id = uqry.create_test_user()
    user = uqry.fetch_by_key(uqry.TEST_EMAIL)
    print(f'{user=}')
    yield  user
    uqry.delete(uqry.TEST_EMAIL)


OK_MINUTES = 5
# a little kludgy to hard-code this to a day but it works for the moment
NOT_OK_MINUTES = 24 * 60  # a day


def time_that_should_be_ok(issue_time):
    return issue_time + akey.get_auth_key_ttl() - timedelta(minutes=OK_MINUTES)


def time_that_should_not_be_ok(issue_time):
    time_now = issue_time + akey.get_auth_key_ttl() + timedelta(minutes=NOT_OK_MINUTES)
    print(f'{issue_time=}')
    print(f'{time_now=}')
    return time_now


def test_set_auth_key(temp_user):
    """
    Test our auth key generation adds the key and issue time fields to the
    user.
    """
    email = temp_user.get(uqry.EMAIL)
    original_key = temp_user.get(uqry.KEY)
    akey.set_auth_key(email)
    user = uqry.fetch_user(email)
    assert isinstance(user.get(uqry.KEY), str)
    assert user.get(uqry.KEY) != original_key
    if is_cicd_env():
        assert True
    else:
        assert now() >= get_issue_time(user)


NOW = 'backendcore.security.utils.now'


def test_is_valid_key(temp_user):
    """
    Test that we can see if a User with a given key is in the table.
    """
    email = temp_user[uqry.EMAIL]
    akey.set_auth_key(email)
    user = uqry.fetch_user(email)
    with mock.patch(NOW) as mock_now:
        mock_now.return_value = time_that_should_be_ok(get_issue_time(user))
        assert akey.is_valid_key(email, user[uqry.KEY])


def test_is_invalid_key():
    """
    Test that we raise an error if we test that a key is valid and no row
    matches the key.
    """
    assert not akey.is_valid_key("fake user", "invalid key")


def test_is_expired_key(temp_user):
    """
    Test that we return False if the user's key has expired.
    """
    email = temp_user[uqry.EMAIL]
    akey.set_auth_key(email)
    with mock.patch(NOW) as mock_now:
        mock_now.return_value = time_that_should_not_be_ok(get_issue_time(temp_user))
        user = uqry.fetch_user(email)
        assert not akey.is_valid_key(email, user[uqry.KEY])


def test_update_key(temp_user):
    """
    Test updating a user's auth key.
    Any key value will do.
    """
    TEST_KEY = '55b748d1-0162-486d-90ab-0d6cd84b4201'
    email = temp_user.get(uqry.EMAIL)
    akey.update_key(email, TEST_KEY)
    updated_user = uqry.fetch_user(email)
    assert updated_user.get(uqry.KEY) == TEST_KEY


def test_get_user_key(temp_user):
    email = temp_user.get(uqry.EMAIL)
    key = akey.get_user_key(email)
    assert key is not None
    assert isinstance(key, str)


def test_get_bad_user_key():
    key = akey.get_user_key('fake key')
    assert key is None


def test_fetch_user_id_by_key(temp_user):
    assert akey.fetch_user_id_by_key(temp_user[uqry.KEY]) is not None
