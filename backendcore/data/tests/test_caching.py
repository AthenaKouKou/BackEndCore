from copy import deepcopy

from unittest.mock import patch

import pytest

import backendcore.data.caching as cach

FLD1 = 'fld1'
FLD2 = 'fld2'
VAL1 = 'val1'
VAL2 = 'val2'
VAL3 = 'val3'
VAL4 = 'val4'

REC1 = {
    FLD1: VAL1,
    FLD2: VAL2,
}

DIFF_KEY_VAL = 'A brand new val'
DIFF_REC = {
    FLD1: DIFF_KEY_VAL,
    FLD2: VAL2,
}

TEST_LIST = [
    REC1,
    {
        FLD1: VAL3,
        FLD2: VAL4,
    },
]

TEMP_DB = 'TempDB'
TEMP_COLLECT = 'TempCollection'

TEST_DCOLLECT = cach.DataCollection(TEMP_DB,
                                    TEMP_COLLECT,
                                    key_fld=FLD1,
                                    sort_fld=FLD2,
                                   )


@pytest.fixture(scope='function')
def new_dcollect():
    return deepcopy(TEST_DCOLLECT)


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
        dcollect = cach.DataCollection(TEMP_DB, TEMP_COLLECT)


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
    assert(len(ret) == 1)


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_fetch_by_fld_val_not_there(mock_fetch, new_dcollect):
    ret = new_dcollect.fetch_by_fld_val(FLD2, 'fake val')
    assert(len(ret) == 0)


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


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_add_duplicate(mock_fetch, new_dcollect):
    with pytest.raises(ValueError):
        # REC1 should be in there already.
        new_dcollect.add(REC1)


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


@patch('backendcore.data.db_connect.fetch_all', autospec=True,
       return_value=TEST_LIST)
def test_clear_cache(mock_fetch, new_dcollect):
    assert new_dcollect.exists(VAL1)
    new_dcollect.clear_cache()
    assert new_dcollect.data_dict is None
