import pytest

import backendcore.data.map as cmap

KEY1 = 'key1'
KEY2 = 'key2'
VAL1 = 'val1'
VAL2 = 'val2'

TEST_NAME = 'Test map'
TEST_VALS = {
    KEY1: VAL1,
    KEY2: VAL2,
}

TEST_MAP = cmap.Map(TEST_NAME, TEST_VALS)


def test_get():
    assert TEST_MAP[KEY1] == VAL1
    assert TEST_MAP[KEY2] == VAL2


def test_get_not_a_code():
    with pytest.raises(KeyError):
        TEST_MAP['not a code']


def test_len():
    # The length of the object should be the same as the dictionary it was
    # created with.
    assert len(TEST_MAP) == len(TEST_VALS)


def test_get_choices():
    # The return should have the same values as the original data:
    assert TEST_MAP.get_choices() == TEST_VALS
    # But not be the same object:
    assert TEST_MAP.get_choices() is not TEST_VALS


def test_is_valid():
    assert TEST_MAP.is_valid(KEY1)
    assert TEST_MAP.is_valid(KEY2)
