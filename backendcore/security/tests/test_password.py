# Copyright 2021 API MixMaster LLC. All rights reserved.
"""
Tests password.py
"""
from datetime import datetime, timedelta
from unittest import mock
import os

import pytest

import backendcore.users.query as uqry
from backendcore.security.settings import PW_RESET_TOK_TTL

import backendcore.security.password as pwd


@pytest.fixture(scope='function')
def temp_user():
    LISTS_IN_DB = os.environ.get('LISTS_IN_DB')
    NO_LISTS_REASON = os.environ.get('NO_LISTS_REASON')
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


def test_check_password(temp_user):
    """
    Tests that we can correctly validate a user's password.
    """
    assert pwd.correct_pw(temp_user.get(uqry.EMAIL),
                          uqry.TEST_PASSWORD)


def test_correct_password_no_user():
    email = 'no_user_has_this_email@koukoudata.com'
    assert not pwd.correct_pw(email, 'some password')


def test_req_pw_reset_token(temp_user):
    """
    Tests that we properly create a password reset token.
    """
    token = pwd.create_pw_reset_token(uqry.TEST_EMAIL)
    print(f'{token=}')
    updated_user = uqry.fetch_user(uqry.TEST_EMAIL)
    assert updated_user[uqry.PW_RES_TOK]


def test_reset_pw(temp_user):
    """
    Tests that we reset a password in the correct circumstances.
    A test like this should never mention salts and so forth!
    """
    email = uqry.TEST_EMAIL
    token = pwd.create_pw_reset_token(email)
    pwd.reset_pw(email, token, 'new pw')
    assert pwd.correct_pw(email, 'new pw')


def test_reset_wrong_token(temp_user):
    """
    Tests that we do not change the user's password if the token is
    invalid.
    """
    orig_pw = temp_user.get(uqry.PASSWORD)
    email = uqry.TEST_EMAIL
    pwd.create_pw_reset_token(email)
    with pytest.raises(ValueError):
        pwd.reset_pw(email=email, token="incorrect", new_pw='new pw')


@pytest.mark.skip('This test is way too complicated.')
def test_expired_pw_reset_tok(temp_user):
    """
    Test that we raise an error if the user's password reset token has expired.
    """
    orig_pw = temp_user[uqry.PASSWORD]
    token = pwd.create_pw_reset_token(uqry.TEST_EMAIL)
    # TODO: The security package should not raise HTTP exceptions.
    with pytest.raises(wz.Unauthorized), mock.patch('backendcore.security.utils.now') as mock_now:
        user = uqry.fetch_user(uqry.TEST_EMAIL)
        mock_now.return_value = user[uqry.PW_RES_TOK_ISS_TIME] + PW_RESET_TOK_TTL + timedelta(
            minutes=1
        )
        pwd.reset_pw(email=uqry.TEST_EMAIL, token=token, new_pw='new pw')
    assert not pwd.correct_pw(user[uqry.EMAIL], 'new pw')
