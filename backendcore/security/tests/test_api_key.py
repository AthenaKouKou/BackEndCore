import pytest

import backendcore.security.api_key as apik

KEY_TOO_SHORT = 'will not work'


def test_num_keys():
    apik.clear_keys()
    assert apik.num_keys() == 0
    apik.add(apik.TEST_KEY)
    assert apik.num_keys() == 1


def test_clear_keys():
    """
    This test is a lot like test_num_keys but that will change as module
    becomes more sophiticated.
    """
    apik.clear_keys()
    assert apik.num_keys() == 0


def test_add():
    apik.add(apik.TEST_KEY)
    assert apik.exists(apik.TEST_KEY)


def test_add_bad_key():
    with pytest.raises(ValueError):
        apik.add(KEY_TOO_SHORT)


def test_add_bad_key_type():
    with pytest.raises(TypeError):
        apik.add(17)


def test_exists():
    """
    This test is a lot like test_add but that will change as module
    becomes more sophiticated.
    """
    apik.add(apik.TEST_KEY)
    assert apik.exists(apik.TEST_KEY)


def test_not_exists():
    assert not apik.exists('do not add this key or this test will fail!')
