"""
This module tests our code for managing API categories.
"""
import random
from copy import deepcopy

import pytest
import pymongo

import backendcore.data.db_connect as dbc

TEST_DB = 'test_db'
TEST_COLLECT = 'test_collect'

RECS_TO_TEST = 10  # 10 is arbitrary!

DEF_FLD = 'fld0'
DEF_VAL = 'def_val'

DEF_PAIR = {DEF_FLD: DEF_VAL}

LIST_FLD = 'a_list'

NEW_FLD = 'fld1'
NEW_VAL = 'flooby!'

BAD_VAL = "Scooby-dooby-doo!"

BIG_INT = 10**32


def rand_fld_val():
    """
    Return this as a str due to Mongo int limits.
    We should only get a duplicate every billion or so tests.
    """
    return str(random.randint(0, BIG_INT))


@pytest.fixture(scope='function')
def some_docs():
    """
    General mongo test fixture.
    Creates a bunch o' docs, then deletes them after test runs.
    """
    for i in range(RECS_TO_TEST):
        dbc.insert_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: f'val{i}'})
    yield
    for i in range(RECS_TO_TEST):
        dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: f'val{i}'})


@pytest.fixture(scope='function')
def a_doc():
    """
    General mongo test fixture.
    Creates one doc, then deletes it after test runs.
    """
    ret = dbc.insert_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: DEF_VAL, LIST_FLD: []})
    yield ret
    dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)


@pytest.fixture(scope='function')
def new_doc():
    """
    General mongo test fixture.
    Creates one doc, but does NOT delete it after test runs:
        needed for testing delete functions!
    """
    dbc.insert_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: DEF_VAL, LIST_FLD: []})


GOOD_ID = '1' * dbc.DB_ID_LEN
BAD_ID = '1' * (dbc.DB_ID_LEN - 1)


def test_is_valid_id():
    assert dbc.is_valid_id(GOOD_ID)


def test_is_not_valid_id():
    assert not dbc.is_valid_id(BAD_ID)


DATE_SAMPLE = '2023-06-06T13:50:23.091Z'
DATE_REC_SAMPLE = {'issue_time': {dbc.DATE_KEY: DATE_SAMPLE}}


def test_extract_date():
    str_date = dbc.extract_date('issue_time', DATE_REC_SAMPLE)
    assert str_date == DATE_SAMPLE


REC_W_ID = {
    dbc.DB_ID: {
        dbc.INNER_DB_ID: '6466b27e3bddcc6a7adc6637'
    },
    'other_field': 1,
}


@pytest.fixture(scope='function')
def rec_w_id():
    return deepcopy(REC_W_ID)


def test_id_handler_without_id(rec_w_id):
    new_rec = dbc._id_handler(rec_w_id, True)
    assert dbc.DB_ID not in new_rec
    assert 'other_field' in new_rec


def test_id_handler_with_id(rec_w_id):
    new_rec = dbc._id_handler(rec_w_id, False)
    assert dbc.DB_ID in new_rec
    assert 'other_field' in new_rec
    assert isinstance(new_rec[dbc.DB_ID], str)


def test_connectDB():
    """
    We should be able to connect to our DB!
    """
    connection = dbc.connectDB()
    assert connection is not None


def test_get_db_variant():
    """
    Test we get the proper DB name: since we are
    running tests, TEST_DB should be true!
    """
    db_var = dbc.get_db_variant(dbc.API_DB)
    assert db_var == dbc.TEST_PREFIX + dbc.API_DB


def test_fetch_by_id(a_doc):
    ret = dbc.fetch_by_id(TEST_DB, TEST_COLLECT, a_doc)
    assert ret is not None


def test_del_by_id(new_doc):
    rec1 = dbc.fetch_one(TEST_DB, TEST_COLLECT)
    rec_id = rec1[str(dbc.DB_ID)]
    dbc.del_by_id(TEST_DB, TEST_COLLECT, rec_id)
    assert dbc.fetch_by_id(TEST_DB, TEST_COLLECT, rec_id) is None


def test_update_fld(a_doc):
    unique_val = rand_fld_val()
    dbc.update_fld(TEST_DB, TEST_COLLECT, DEF_PAIR,
                   DEF_FLD, unique_val)
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) == 1


def test_update_doc(a_doc):
    unique_val = rand_fld_val()
    dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR,
                   {DEF_FLD: unique_val, LIST_FLD: ['something']})
    recs = dbc.select(TEST_DB, TEST_COLLECT,
                      filters={DEF_FLD: unique_val, LIST_FLD: ['something']})
    assert len(recs) == 1


def test_select_cursor_no_filter(some_docs):
    """
    This should return all records in a collection.
    We test with >= since someone may have left other docs
    in our test_db.
    """
    cursor = dbc.select_cursor(TEST_DB, TEST_COLLECT, filters={})
    assert isinstance(cursor, pymongo.cursor.Cursor)


def test_select_no_filter(some_docs):
    """
    This should return all records in a collection.
    We test with >= since someone may have left other docs
    in our test_db.
    """
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={})
    assert len(recs) >= RECS_TO_TEST


def test_select_w_filter(some_docs):
    """
    This should return all records in a collection matching the
    filter.
    This record should be unique except for a 1 in BIG_INT
    chance. Enough for our lifetimes.
    """
    unique_val = rand_fld_val()
    dbc.insert_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) == 1


def test_fetch_one_no_filter(a_doc):
    """
    Tests that a fetch with no filter retieves the rec we inserted
    in the fixture.
    """
    rec = dbc.fetch_one(TEST_DB, TEST_COLLECT, filters={})
    assert rec is not None


def test_fetch_one_bad_filter(a_doc):
    """
    Tests that a fetch with a bad filter fails.
    """
    rec = dbc.fetch_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert rec is None


def test_fetch_one_good_filter(a_doc):
    """
    Tests that a fetch with a good filter works.
    """
    rec = dbc.fetch_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert rec is not None


def test_del_one_that_exists(a_doc):
    """
    Make sure deleting a doc that exists deletes 1 record.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert result.deleted_count == 1


def test_del_one_that_dont_exist(a_doc):
    """
    Make sure deleting a doc that doesn't exist deletes 0 records.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert result.deleted_count == 0


def test_del_many(a_doc):
    """
    Make sure deleting many docs leaves none behind.
    """
    dbc.del_many(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.fetch_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR) is None


def test_delete_success(a_doc):
    """
    Make sure that deleted one can properly detect if a record has been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.delete_success(result) == True


def test_delete_no_success(a_doc):
    """
    Make sure that deleted one can properly detect if a record has not been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert dbc.delete_success(result) == False


def test_num_deleted_single(a_doc):
    """
    Make sure that num_deleted can properly detect if a single record has been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert dbc.num_deleted(result) == 1


def test_num_deleted_multiple(some_docs):
    """
    Make sure that num_deleted can properly detect if several records have been
    deleted.
    """
    result = dbc.del_many(TEST_DB, TEST_COLLECT, filters={})
    assert dbc.num_deleted(result) > 1


def test_num_deleted_none(a_doc):
    """
    Make sure that num_deleted can properly detect if no records have been
    deleted.
    """
    result = dbc.del_one(TEST_DB, TEST_COLLECT, filters={DEF_FLD: BAD_VAL})
    assert dbc.num_deleted(result) == 0


def test_update_success(a_doc):
    """
    Make sure that updated one can properly detect if a record has been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR, DEF_PAIR)
    assert dbc.update_success(result) == True


def test_update_no_success(a_doc):
    """
    Make sure that updated one can properly detect if a record has not been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert dbc.update_success(result) == False


def test_num_updated_single(a_doc):
    """
    Make sure that num_updated can properly detect if a single record has been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, DEF_PAIR,
                            {DEF_FLD: 'new val'})
    assert dbc.num_updated(result) == 1


def test_num_updated_multiple(some_docs):
    """
    Make sure that num_updated can properly detect if several records have been
    updated.
    """
    result = dbc.update_fld_for_many(TEST_DB, TEST_COLLECT, {}, 'new field', 'new val')
    assert dbc.num_updated(result) > 1


def test_num_updated_none(a_doc):
    """
    Make sure that num_updated can properly detect if no records have been
    updated.
    """
    result = dbc.update_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: BAD_VAL}, DEF_PAIR)
    assert dbc.num_updated(result) == 0


def test_add_fld_to_all(some_docs):
    """
    Testing updating all records with some new field.
    """
    dbc.add_fld_to_all(TEST_DB, TEST_COLLECT, NEW_FLD, NEW_VAL)
    for i in range(RECS_TO_TEST):
        rec = dbc.fetch_one(TEST_DB, TEST_COLLECT)
        assert rec[NEW_FLD] == NEW_VAL


def test_append_to_list(a_doc):
    """
    Test appending to an interior doc list.
    `a_doc` initiliazes an empty list, so our new val should be
    at `[LIST_FLD][0]`.
    """
    dbc.append_to_list(TEST_DB, TEST_COLLECT, DEF_FLD, DEF_VAL,
                       LIST_FLD, 1)  # any old val will do!
    rec = dbc.fetch_one(TEST_DB, TEST_COLLECT, filters=DEF_PAIR)
    assert rec[LIST_FLD][0] == 1


def test_rename_fld(some_docs):
    """
    Test renaming a field.
    """
    dbc.rename(TEST_DB, TEST_COLLECT, {DEF_FLD: NEW_FLD})
    for i in range(RECS_TO_TEST):
        rec = dbc.fetch_one(TEST_DB, TEST_COLLECT)
        assert rec[NEW_FLD]


def test_insert_doc():
    """
    There should not be more than one of these after insert,
    but let's test just that there is at least one.
    """
    unique_val = rand_fld_val()
    dbc.insert_doc(TEST_DB, TEST_COLLECT, {DEF_FLD: unique_val})
    recs = dbc.select(TEST_DB, TEST_COLLECT, filters={DEF_FLD: unique_val})
    assert len(recs) >= 1