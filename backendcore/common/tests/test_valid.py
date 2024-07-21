
"""
Test suite for validators.
"""

import backendcore.common.valid as vld

GOOD_URL = 'https://google.com/'
GOOD_EMAIL = 'fred@sunsetpark.com'


def test_is_valid_url():
    assert vld.is_valid_url(GOOD_URL)


def test_is_not_valid_url():
    assert not vld.is_valid_url('Some rubbish that is not a URL.')


def test_is_valid_email():
    assert vld.is_valid_email(GOOD_EMAIL)


def test_is_not_valid_email():
    assert not vld.is_valid_email('Not an email address!')
