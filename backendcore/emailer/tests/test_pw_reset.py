"""
Tests for pw_rest module.
"""
from unittest.mock import patch

import pytest

import backendcore.emailer.pw_reset as pwr

BACKENDCORE_EMAILER = 'backendcore.emailer'

TEST_EMAIL = 'gcallah@mac.com'
ABRITARY_RESET_TIME = 10
FAKE_RESET_TOKEN = 'kjshjkaskashf'
BAD_METHOD = 'Bad method!'

FAKE_BASE_URL = 'https://prod.server.com'
FAKE_TEST_URL = 'https://test.server.com'


def test_is_valid_mail_method():
    for method in pwr.VALID_MAIL_METHODS:
        assert pwr.is_valid_mail_method(method)


def test_is_not_valid_mail_method():
    assert not pwr.is_valid_mail_method(BAD_METHOD)


def test_check_for_slash():
    assert pwr.check_for_slash(FAKE_BASE_URL).endswith('/')


@patch(f'{BACKENDCORE_EMAILER}.pw_reset.get_base_url',
       autospec=True, return_value=FAKE_BASE_URL)
def test_base_url_test_false(mock_get_base_url):
    assert pwr.set_base_url(False).startswith(FAKE_BASE_URL)


@patch(f'{BACKENDCORE_EMAILER}.pw_reset.get_test_url',
       autospec=True, return_value=FAKE_TEST_URL)
def test_base_url_test_true(mock_get_test_url):
    assert pwr.set_base_url(True).startswith(FAKE_TEST_URL)


@patch(f'{BACKENDCORE_EMAILER}.api_send.send_mail',
       autospec=True, return_value='Not none')
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
