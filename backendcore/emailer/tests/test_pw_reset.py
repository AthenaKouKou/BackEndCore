"""
Tests for pw_rest module.
"""
from unittest.mock import patch

import pytest

import backendcore.emailer.pw_reset as pwr

TEST_EMAIL = 'gcallah@mac.com'
ABRITARY_RESET_TIME = 10
FAKE_RESET_TOKEN = 'kjshjkaskashf'
BAD_METHOD = 'Bad method!'

NEW_BASE_URL = 'https://some.server.com'


def test_set_base_url_none():
    assert pwr.BASE_URL in pwr.set_base_url(None)


def test_set_base_url_not_none():
    assert NEW_BASE_URL in pwr.set_base_url(NEW_BASE_URL)


@patch('backendcore.emailer.api_send.send_mail',
       autospec=True, return_val='Not none')
def test_send_pw_reset(mock_send_mail):
    ret = pwr.send_pw_reset(FAKE_RESET_TOKEN, TEST_EMAIL, ABRITARY_RESET_TIME)
    assert ret is not None


def test_send_pw_reset_no_tok():
    with pytest.raises(ValueError):
        pwr.send_pw_reset('', TEST_EMAIL, ABRITARY_RESET_TIME)


def test_send_pw_reset_bad_method():
    with pytest.raises(ValueError):
        pwr.send_pw_reset(FAKE_RESET_TOKEN, TEST_EMAIL,
                          ABRITARY_RESET_TIME, method=BAD_METHOD)


def test_is_valid_mail_method():
    for method in pwr.VALID_MAIL_METHODS:
        assert pwr.is_valid_mail_method(method)


def test_is_not_valid_mail_method():
    assert not pwr.is_valid_mail_method(BAD_METHOD)
