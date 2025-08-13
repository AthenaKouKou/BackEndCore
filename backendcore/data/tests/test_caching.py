from copy import deepcopy

from unittest.mock import patch

import pytest

import backendcore.data.caching as cach

KEY_FLD = 'fld1'
FLD2 = 'fld2'
VAL1 = 'val1'
VAL2 = 'val2'
VAL3 = 'val3'
VAL4 = 'val4'

REC1 = {
    KEY_FLD: VAL1,
    FLD2: VAL2,
}

REC2 = {
    KEY_FLD: VAL3,
    FLD2: VAL4,
}

DIFF_KEY_VAL = 'A brand new val'
DIFF_REC = {
    KEY_FLD: DIFF_KEY_VAL,
    FLD2: VAL2,
}

TEST_LIST = [
    REC1,
    REC2,
]

TEMP_DB = 'TempDB'
TEMP_COLLECT = 'TempCollection'
TEMP_KEY_COLLECT = 'TempKeyCollection'

TEST_DCOLLECT = cach.DataCollection(TEMP_DB,
                                    TEMP_COLLECT,
                                    key_fld=KEY_FLD,
                                    sort_fld=FLD2,
                                    )

TEST_KEYFLD_COLLECT = cach.DataCollection(TEMP_DB,
                                          TEMP_KEY_COLLECT,
                                          key_fld=KEY_FLD,
                                          sort_fld=FLD2,
                                          )


@pytest.fixture(scope='function')
def new_dcollect():
    return deepcopy(TEST_DCOLLECT)


@pytest.fixture(scope='function')
def new_keyfld_collect():
    return deepcopy(TEST_KEYFLD_COLLECT)


@pytest.fixture(scope='function')
def some_recs(new_dcollect):
    new_dcollect.add(REC1)
    new_dcollect.add(REC2)
    yield new_dcollect
    new_dcollect.delete(VAL1)
    new_dcollect.delete(VAL3)


FLD_NM = 'fld1'


def test_can_do_math_with_int():
    record = {FLD_NM: 17}
    assert cach.can_do_math(record, FLD_NM)


def test_can_do_math_with_float():
    record = {FLD_NM: 3.14159}
    assert cach.can_do_math(record, FLD_NM)


def test_cant_do_math_with_str():
    record = {FLD_NM: 'not a good value for math'}
    assert not cach.can_do_math(record, FLD_NM)


def test_cant_do_math_with_missing_fld():
    record = {'the wrong field name': 'no good'}
    assert not cach.can_do_math(record, FLD_NM)


def test_class_is_registered(new_dcollect):
    assert cach.DataCollection.is_registered(TEMP_COLLECT)


def test_class_is_not_registered(new_dcollect):
    assert not cach.DataCollection.is_registered('Not registered!')


def test_func_is_registered(new_dcollect):
    assert cach.is_registered(TEMP_COLLECT)


def test_func_is_not_registered(new_dcollect):
    assert not cach.is_registered('Not registered!')


def test_class_get_cache(new_dcollect):
    assert isinstance(cach.DataCollection.get_cache(TEMP_COLLECT),
                      cach.DataCollection)


def test_class_get_cache_not_there(new_dcollect):
    assert cach.DataCollection.get_cache('Not registered!') is None


def test_func_get_cache(new_dcollect):
    assert isinstance(cach.get_cache(TEMP_COLLECT), cach.DataCollection)


def test_func_get_cache_not_there(new_dcollect):
    assert cach.get_cache('Not registered!') is None


def test_init():
    dcollect = cach.DataCollection(TEMP_DB, 'Unique collection')
    assert isinstance(dcollect, cach.DataCollection)


def test_init_dup_collection(new_dcollect):
    with pytest.raises(ValueError):
        cach.DataCollection(TEMP_DB, TEMP_COLLECT)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_list(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_list()
    assert isinstance(ret, list)
    # make sure we are returning a new list, not the cache:
    assert id(ret) != id(new_dcollect.data_list)
    assert len(ret) == len(TEST_LIST)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=deepcopy(TEST_LIST))
def test_add_to_cache(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_list()
    new_dcollect._add_to_cache(DIFF_REC)
    assert len(new_dcollect) > len(ret)
    new_dcollect.clear_cache()


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_dict(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_dict()
    print(f'{ret=}')
    assert isinstance(ret, dict)
    # make sure we are returning a new list, not the cache:
    assert id(ret) != id(new_dcollect.data_dict)
    assert len(ret) == len(TEST_LIST)
    assert VAL1 in ret
    assert VAL3 in ret


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_keys(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_keys()
    assert isinstance(ret, list)
    assert len(ret) == len(TEST_LIST)
    assert VAL1 in ret
    assert VAL3 in ret


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_get_choices(mock_fetch, new_dcollect):
    ret = new_dcollect.get_choices()
    assert isinstance(ret, dict)
    assert len(ret) == len(TEST_LIST)
    assert VAL1 in ret
    assert VAL3 in ret


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_by_key(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_by_key(VAL1)
    assert ret == REC1


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_by_key_not_there(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_by_key('Not a value in the list!')
    assert ret is None


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_by_fld_val(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_by_fld_val(FLD2, VAL2)
    print(f'{ret=}')
    assert (len(ret) == 1)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_by_fld_val_not_there(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_by_fld_val(FLD2, 'fake val')
    assert (len(ret) == 0)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_exists(mock_fetch, new_dcollect):
    assert new_dcollect.exists(VAL1)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_exists_not_there(mock_fetch, new_dcollect):
    assert not new_dcollect.exists('Not a value in the list!')


def test_add(new_dcollect):
    """
    Can't mock fetch here.
    """
    new_dcollect.clear_cache()
    new_dcollect.add(DIFF_REC)
    assert new_dcollect.exists(DIFF_KEY_VAL)
    new_dcollect.delete(DIFF_KEY_VAL)


def test_add_keyfld_rec(new_keyfld_collect):
    """
    Same as above but checks we can properly add records that use database ids
    as key field and don't provide a keyfield upon creation
    """
    new_keyfld_collect.clear_cache()
    new_keyfld_collect.add(DIFF_REC)
    assert new_keyfld_collect.exists(DIFF_KEY_VAL)
    new_keyfld_collect.delete(DIFF_KEY_VAL)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_add_duplicate(mock_fetch, new_dcollect):
    with pytest.raises(ValueError):
        # REC1 should be in there already.
        new_dcollect.add(REC1)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_add_no_key_fld(mock_fetch, new_dcollect):
    REC_NO_KEY = deepcopy(REC1)
    REC_NO_KEY.pop(KEY_FLD)
    with pytest.raises(ValueError):
        new_dcollect.add(REC_NO_KEY)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_delete(mock_fetch, new_dcollect):
    assert new_dcollect.delete(VAL1)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_delete_not_there(mock_fetch, new_dcollect):
    with pytest.raises(ValueError):
        new_dcollect.delete('Not an existing key!')


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
@patch('backendcore.data.db_connect.update_success', autospec=True,
       return_value=True)
def test_update(mock_fetch, mock_update, new_dcollect):
    assert new_dcollect.update(VAL1, DIFF_REC)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_update_not_there(mock_fetch, new_dcollect):
    with pytest.raises(ValueError):
        new_dcollect.update('Not an existing key!', DIFF_REC)


def test_update_fld(some_recs):
    NEW_VAL = 'new value'
    ret = some_recs.update_fld(VAL1, FLD2, NEW_VAL)
    assert ret
    assert some_recs.fetch_by_key(VAL1)[FLD2] == NEW_VAL


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_clear_cache(mock_fetch, new_dcollect):
    assert new_dcollect.exists(VAL1)
    new_dcollect.clear_cache()
    assert new_dcollect.data_dict is None
