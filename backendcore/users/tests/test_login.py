"""
Tests login.py
"""
import pytest
import os

import backendcore.common.time_fmts as tfmt
import backendcore.users.query as uqry

from backendcore.users.login import login


@pytest.fixture(scope='function')
def temp_user():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    NO_LISTS_REASON = "DB does not support lists as values"
    if LISTS_IN_DB == '0' or not LISTS_IN_DB:
        pytest.skip(NO_LISTS_REASON)
    try:
        uqry.delete(uqry.TEST_EMAIL)
    except Exception:
        print('User was not already in DB')
    mongo_id = uqry.create_test_user()
    user = uqry.fetch_by_key(uqry.TEST_EMAIL)
    yield  user
    uqry.delete(uqry.TEST_EMAIL)



def test_login_success(temp_user):
    """
    Tests a successful login.
    """
    assert login(temp_user[uqry.EMAIL], uqry.TEST_PASSWORD) is not None


def test_login_no_user():
    """
    Test that we raise an error when client tries to login a non-existent user.
    """
    email = 'kshfkjhfsdfhgkjs@skajhsfjkSHEF.COM'
    assert login(email, 'some password') is None


def test_login_bad_pw(temp_user):
    """
    Test that we return None when we get a bad password.
    """
    assert login(temp_user[uqry.EMAIL], 'wrong password') is None


def test_record_login(temp_user):
    """
    Test that when a user logs-in, we record the date.
    """
    email = temp_user[uqry.EMAIL]
    today = tfmt.get_today()
    login(email, uqry.TEST_PASSWORD)
    user = uqry.fetch_user(email)
    assert today in user[uqry.LOGINS]
