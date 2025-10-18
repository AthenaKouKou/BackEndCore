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


def test_bad_name_init():
    with pytest.raises(TypeError):
        cmap.Map(17, TEST_VALS)


def test_getitem_dunder():
    assert TEST_MAP[KEY1] == VAL1
    assert TEST_MAP[KEY2] == VAL2


def test_get_not_a_code():
    with pytest.raises(KeyError):
        TEST_MAP['not a code']


def test_get_name():
    assert TEST_MAP.get_name() == TEST_NAME


def test_cannot_change_data():
    # This is an immutable dictionary type!
    with pytest.raises(TypeError):
        TEST_MAP[KEY1] = 'a new value'


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


def test_is_not_valid():
    assert not TEST_MAP.is_valid('not a key')


def test_get():
    ret = TEST_MAP.get(KEY1)
    assert ret == VAL1


def test_get_default():
    ret = TEST_MAP.get('not a key', default=17)
    assert ret == 17


def test_get_no_result():
    ret = TEST_MAP.get("Not a key")
    assert ret is None


TEST_BIMAP = cmap.BiMap(TEST_NAME, TEST_VALS)
BAD_BIMAP_DICT = {
    KEY1: {'dict is': 'not hashable'},
    KEY2: VAL2,
}


def test_bimap_is_a_map():
    assert isinstance(TEST_BIMAP, cmap.Map)


def test_catch_val_not_hashable():
    with pytest.raises(TypeError):
        cmap.BiMap(TEST_NAME, BAD_BIMAP_DICT)


def test_is_rev_valid():
    assert TEST_BIMAP.is_rev_valid(VAL1)
    assert TEST_BIMAP.is_rev_valid(VAL2)


def test_is_not_valid():
    assert not TEST_BIMAP.is_rev_valid('not a val')


def test_rev_get():
    assert TEST_BIMAP.rev_get(VAL1) == KEY1
    assert TEST_BIMAP.rev_get(VAL2) == KEY2


def test_rev_get_default():
    ret = TEST_BIMAP.rev_get('not a val', default=17)
    assert ret == 17
