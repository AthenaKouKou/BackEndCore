import pytest

import backendcore.common.hashing as hsh


def test_hash_str_and_salt():
    """
    Tests that we receive a string from the hash_str_and_salt function.
    """
    assert isinstance(hsh.hash_str_and_salt('pswd', 'salt'), str)


def test_hash_str_and_salt_wrong_str():
    """
    Tests that sending something other than a string to hash to the hash_str_and_salt function
    returns a TypeError.
    """
    with pytest.raises(TypeError):
        hsh.hash_str_and_salt(123, 'salt')


def test_hash_str_and_salt_no_str():
    """
    Tests that sending an empty string to the hash_str_and_salt function returns a ValueError
    """
    with pytest.raises(ValueError):
        hsh.hash_str_and_salt('', 'salt')


def test_hash_str_and_salt_wrong_salt():
    """
    Tests that a salt that isn't a string sent to the hash_str_and_salt function
    returns a TypeError.
    """
    with pytest.raises(TypeError):
        hsh.hash_str_and_salt('pswd', 123)
