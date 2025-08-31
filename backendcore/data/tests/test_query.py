"""
Test module for our caching functions.
"""
from copy import deepcopy
from unittest.mock import patch
import pytest

import backendcore.data.query as qry


KEY1 = 'key1'
KEY2 = 'key2'
KEY3 = 'key3'
FLD1 = 'fld1'
FLD2 = 'fld2'
VAL1 = 'val1'
VAL2 = 'val2'
VAL3 = 'val3'
VAL4 = 'val4'

TEST_DICT_LISTS = {
    KEY1: {
        FLD1: [VAL1, VAL2],
    },
    KEY2: {
        FLD2: [VAL3, VAL4],
    },
}

TEST_DICT_VALS = {
    KEY1: {
        FLD1: VAL1,
        FLD2: VAL2,
    },
    KEY2: {
        FLD1: VAL3,
        FLD2: VAL4,
    },
    KEY3: {
        FLD1: VAL1,
        FLD2: VAL4,
    },
}

TEST_LIST = [
    {
        FLD1: VAL1,
        FLD2: VAL2,
    },
    {
        FLD1: VAL3,
        FLD2: VAL4,
    },
]

TEST_RECS_KEY_FLD = 'x'

TEST_RECS = [
    {TEST_RECS_KEY_FLD: 17, 'y': 18},
    {TEST_RECS_KEY_FLD: 19, 'y': 20},
]


@patch('backendcore.data.db_connect.read', autospec=True,
       return_value=TEST_LIST)
def test_fetch_list(mock_read):
    ret = qry.fetch_list('Some DB name', 'Some collection name')
    assert isinstance(ret, list)
    assert len(ret) == len(TEST_LIST)


def test_regex_search():
    res = qry.regex_search(FLD1, VAL1, TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res


def test_regex_search_diff_case():
    res = qry.regex_search(FLD1, VAL1.upper(), TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res


def test_regex_search_partial_match():
    res = qry.regex_search(FLD1, '1', TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res


def test_regex_search_no_match():
    assert len(qry.regex_search(FLD1, 'Not in the data!', TEST_DICT_VALS)) == 0


def test_fetch_by_fld_val():
    res = qry.fetch_by_fld_val(FLD1, VAL1,
                               TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res


def test_fetch_by_fld_val_list():
    res = qry.fetch_by_fld_val(FLD1, VAL1,
                               TEST_DICT_LISTS,
                               test_membership=True)
    assert KEY1 in res
    assert KEY2 not in res


def test_get_fld():
    assert qry.get_fld(TEST_DICT_VALS, KEY1, FLD1) == VAL1


def test_get_fld_not_there():
    assert qry.get_fld(TEST_DICT_VALS, KEY1, 'Not a field name') is None


TEST_LIST = [
    {'key_nm': KEY1, 'val_nm': VAL1, 'some_other_fld': 'some_val'},
    {'key_nm': KEY2, 'val_nm': VAL2, 'some_other_fld': 'some_val'},
]


def test_get_choices():
    choices = qry.get_choices(TEST_LIST, 'key_nm', 'val_nm')
    assert isinstance(choices, dict)
    assert choices[KEY1] == VAL1
    assert choices[KEY2] == VAL2


def test_list_to_dict():
    recs = TEST_RECS
    new_dict = qry.list_to_dict('x', recs, del_key=True)
    assert new_dict[17] == {'y': 18}
    assert new_dict[19] == {'y': 20}


@pytest.mark.filterwarnings("ignore:A record")
def test_list_to_dict_no_key_fld():
    recs = deepcopy(TEST_RECS)
    recs[0].pop(TEST_RECS_KEY_FLD)
    new_dict = qry.list_to_dict(TEST_RECS_KEY_FLD, recs, del_key=False)
    assert new_dict[19] == {'x': 19, 'y': 20}


def test_list_to_dict_keep_key():
    recs = TEST_RECS
    new_dict = qry.list_to_dict('x', recs, del_key=False)
    assert new_dict[17] == {'x': 17, 'y': 18}
    assert new_dict[19] == {'x': 19, 'y': 20}


def test_make_combined_key():
    combined_key = qry.make_combined_key(TEST_RECS[0], 'x', 'y')
    assert combined_key == (17, 18)


def test_make_combined_key_str():
    combined_key = qry.make_combined_key_str(TEST_RECS[0], 'x', 'y')
    assert combined_key == '1718'


def test_list_to_dict_multi_key():
    recs = TEST_RECS
    new_dict = qry.list_to_dict_multi_key('x', 'y', recs)
    assert new_dict[(17, 18)] == {'x': 17, 'y': 18}
    assert new_dict[(19, 20)] == {'x': 19, 'y': 20}


def test_list_to_dict_multi_key_stringify():
    recs = TEST_RECS
    new_dict = qry.list_to_dict_multi_key('x', 'y', recs, stringify=True)
    assert new_dict['1718'] == {'x': 17, 'y': 18}
    assert new_dict['1920'] == {'x': 19, 'y': 20}


def test_regex_intersect_search():
    fld_dict = {
        FLD1: VAL1,
        FLD2: VAL2,
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res
    assert KEY3 not in res


def test_regex_intersect_search_diff_case():
    fld_dict = {
        FLD1: VAL1.upper(),
        FLD2: VAL2,
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res
    assert KEY3 not in res


def test_regex_intersect_search_partial_match():
    fld_dict = {
        FLD1: VAL1[0:1],
        FLD2: VAL2,
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res
    assert KEY3 not in res


def test_regex_intersect_search_mulitple_partial_match():
    fld_dict = {
        FLD1: VAL1[0:1],
        FLD2: VAL2[0:1],
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 in res
    assert KEY3 in res


def test_regex_intersect_search_multiple_fld_match_single_all():
    fld_dict = {
        FLD1: VAL1,
        FLD2: VAL4,
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 not in res
    assert KEY2 not in res
    assert KEY3 in res


def test_regex_intersect_search_no_match():
    fld_dict = {
        FLD1: 'fakeval',
        FLD2: 'otherval',
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 not in res
    assert KEY2 not in res
    assert KEY3 not in res
    assert len(res) == 0


def test_regex_intersect_search_none_fld():
    fld_dict = {
        FLD1: VAL1,
        FLD2: None,
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 in res
    assert KEY2 not in res
    assert KEY3 in res


def test_regex_intersect_search_nonexistant_fld():
    fld_dict = {
        "fake_fld": "random val"
    }
    res = qry.regex_intersect_search(fld_dict, TEST_DICT_VALS)
    assert KEY1 not in res
    assert KEY2 not in res
    assert KEY3 not in res
