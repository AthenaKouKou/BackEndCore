import os

import backendcore.env.env_utils as envu
import unittest.mock as mock

TEST_VAR = 'TEST_FLAG_ON_VAR'

@mock.patch.dict(os.environ, {}, clear=True)
def test_flag_not_set():
    """
    Tests if the env var is not set is_flag_on(..) returns False.
    """
    assert not envu.is_flag_on(TEST_VAR)


"""
Tests that if the env var is a Python True equivalent, we return True.
"""


def test_is_flag_on_some_str():
    with mock.patch.dict(
        os.environ,
        {TEST_VAR: 'some string'},
        clear=True):
        assert envu.is_flag_on(TEST_VAR)


def test_is_flag_on_some_num():
    with mock.patch.dict(
        os.environ,
        {TEST_VAR: '46'},
        clear=True):
        assert envu.is_flag_on(TEST_VAR)


def test_is_flag_on_one():
    with mock.patch.dict(
        os.environ,
        {TEST_VAR: envu.FLAG_ON},
        clear=True):
        assert envu.is_flag_on(TEST_VAR)


"""
Tests if the env var is a Python False equivalent, we
return False
"""


def test_flag_not_on_empty_str():
    with mock.patch.dict(
        os.environ,
        {TEST_VAR: ''},
        clear=True):
        assert not envu.is_flag_on(TEST_VAR)


def test_flag_not_on_zero():
    with mock.patch.dict(
        os.environ,
        {TEST_VAR: envu.FLAG_OFF},
        clear=True):
        assert not envu.is_flag_on(TEST_VAR)


def test_is_cicd_env():
    with mock.patch.dict(
        os.environ,
        {envu.CICD_VAR: 'val'},
        clear=True):
        assert envu.is_cicd_env()


def test_is_not_cicd_env():
    with mock.patch.dict(
        os.environ,
        {envu.CICD_VAR: '0'},
        clear=True):
        assert not envu.is_cicd_env()
